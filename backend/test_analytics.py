from services.analytics_engine import generate_insights
d = generate_insights()
hs = d["health_score"]
print("Score:", hs["score"], hs["grade"])
print("Risks:", len(d["stock_risks"]))
print("Actions:", len(d["actions"]))
print("Customers:", d["customers"]["total_customers"])
print("Categories:", len(d["categories"]))
print("OK")
