# Claude
All Claude Code work
import requests, json, csv

KEY = "fce8c4d5b3011b4f41924fcbe30b245bb9b793ff3d48bd9003b20e4b7f52bcee"
HEADERS = {"Content-Type": "application/json"}

# Step 1: Pull firms in FL/NY with AUM $50M-$100M
firm_res = requests.post(
    f"<https://api.sec-api.io/form-adv/firm?token={KEY}>",
    headers=HEADERS,
    json={
        "query": "MainAddr.state:(FL OR NY) AND Info.totalRgltdAum:[50000000 TO 100000000]",
        "from": "0",
        "size": "100",
        "sort": [{"Info.totalRgltdAum": {"order": "desc"}}]
    }
)

print("Firm query status:", firm_res.status_code)
firm_json = firm_res.json()
print("Firm response keys:", list(firm_json.keys()))

firms = firm_json.get("filings", [])
print(f"Found {len(firms)} firms")

if not firms:
    print("No firms returned. Full response:")
    print(json.dumps(firm_json, indent=2))
    raise SystemExit

firm_map = {}
for f in firms:
    info = f.get("Info") or {}
    crd = str(info.get("CrdNb") or f.get("FirmCrdNb") or "")
    if crd:
        firm_map[crd] = {
            "name": info.get("BusNm") or info.get("LegalNm") or "",
            "aum": info.get("totalRgltdAum") or info.get("TotalRgltdAum") or "",
            "state": (f.get("MainAddr") or {}).get("state", ""),
            "city": (f.get("MainAddr") or {}).get("city", ""),
        }

print(f"Mapped {len(firm_map)} firms with CRD numbers")

# Step 2: Pull individual IA reps
advisers = []
crds = list(firm_map.keys())
BATCH = 20

for i in range(0, len(crds), BATCH):
    batch = crds[i:i+BATCH]
    org_clause = " OR ".join([f"CrntEmps.CrntEmp.orgPK:{c}" for c in batch])

    try:
        ind_res = requests.post(
            f"<https://api.sec-api.io/form-adv/individual?token={KEY}>",
            headers=HEADERS,
            json={
                "query": f"({org_clause}) AND CrntEmps.CrntEmp.CrntRgstns.CrntRgstn.regCat:RA",
                "from": "0",
                "size": "200",
                "sort": [{"id": {"order": "desc"}}]
            }
        )
        filings = ind_res.json().get("filings", [])
    except Exception as e:
        print(f"Batch {i} failed: {e}")
        continue

    for ind in filings:
        try:
            info = ind.get("Info") or {}
            name = " ".join(filter(None, [info.get("firstNm"), info.get("midNm"), info.get("lastNm")]))
            crd_num = info.get("indvlPK")
            link = info.get("link") or (f"<https://adviserinfo.sec.gov/individual/summary/{crd_num}>" if crd_num else "")

            emps = (ind.get("CrntEmps") or {}).get("CrntEmp", [])
            if not isinstance(emps, list): emps = [emps]

            for emp in emps:
                if not isinstance(emp, dict): continue
                org_pk = str(emp.get("orgPK", ""))
                firm = firm_map.get(org_pk)
                if not firm: continue

                regs = (emp.get("CrntRgstns") or {}).get("CrntRgstn", [])
                if not isinstance(regs, list): regs = [regs]
                regs = [r for r in regs if isinstance(r, dict)]

                if not any(r.get("regCat") == "RA" for r in regs): continue
                is_dual = any(r.get("regCat") == "BR" for r in regs)
                reg_states = ", ".join(set(r.get("regAuth", "") for r in regs if r.get("st") == "APPROVED"))

                exams = (ind.get("Exms") or {}).get("Exm", [])
                if not isinstance(exams, list): exams = [exams]
                exams = [e for e in exams if isinstance(e, dict)]
                exam_str = ", ".join(e.get("exmCd", "") for e in exams)

                advisers.append({
                    "Name": name or "N/A",
                    "CRD": crd_num or "",
                    "Firm": firm["name"],
                    "Firm AUM": firm["aum"],
                    "City": firm["city"],
                    "State": firm["state"],
                    "Reg States": reg_states,
                    "Exams": exam_str,
                    "Type": "IA + BD" if is_dual else "IA Only",
                    "IAPD Link": link,
                })
        except Exception as e:
            print(f"Skipped one record due to error: {e}")
            continue

    print(f"Processed {min(i+BATCH, len(crds))}/{len(crds)} firms — {len(advisers)} reps so far")

# Deduplicate
seen = set()
unique = []
for a in advisers:
    key = f"{a['CRD']}-{a['Firm']}"
    if key not in seen:
        seen.add(key)
        unique.append(a)

print(f"\nTotal unique advisers: {len(unique)}")

if not unique:
    print("No advisers found. Check the firm response printed above for correct field names.")
else:
    FIELDS = ["Name", "CRD", "Firm", "Firm AUM", "City", "State", "Reg States", "Exams", "Type", "IAPD Link"]
    with open("ia_advisers_FL_NY.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(unique)
    print("Exported to ia_advisers_FL_NY.csv")
