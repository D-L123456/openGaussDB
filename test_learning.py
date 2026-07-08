import asyncio
import httpx

API = "http://127.0.0.1:8000"

async def main():
    results = []
    async with httpx.AsyncClient(base_url=API, timeout=60) as c:

        # 1
        print("=== 1. Backend Health ===")
        try:
            r = await c.get("/api/health")
            assert r.status_code == 200 and r.json()["status"] == "ok"
            results.append(("Health", "PASS")); print("PASS")
        except Exception as e:
            results.append(("Health", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 2
        print("\n=== 2. Events API ===")
        try:
            r = await c.post("/api/learning/events", json={"event_type": "challenge_start", "level": 1})
            assert r.status_code == 200
            results.append(("Events API", "PASS")); print(f"PASS: {r.json()['id'][:8]}")
        except Exception as e:
            results.append(("Events API", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 3
        print("\n=== 3. Profile API ===")
        try:
            r = await c.get("/api/learning/profile")
            assert r.status_code == 200 and "ability_scores" in r.json()
            results.append(("Profile API", "PASS")); print(f"PASS: style={r.json()['learning_style']}")
        except Exception as e:
            results.append(("Profile API", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 4: Challenge pass boost
        print("\n=== 4. Challenge Pass → Ability Boost ===")
        try:
            r1 = await c.post("/api/learning/events", json={"event_type": "challenge_pass", "level": 1, "detail": {"attempts": 1, "duration_seconds": 120}})
            assert r1.status_code == 200
            r2 = await c.get("/api/learning/profile")
            scores = r2.json()["ability_scores"]
            db_design = scores.get("数据库设计", 10)
            assert db_design > 10, f"Not boosted: {scores}"
            results.append(("Challenge Boost", "PASS")); print(f"PASS: 数据库设计={db_design}")
        except Exception as e:
            results.append(("Challenge Boost", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 5: Error → weak points
        print("\n=== 5. Error → Weak Points ===")
        try:
            r1 = await c.post("/api/learning/events", json={"event_type": "challenge_error", "level": 2, "part": 3, "detail": {"category": "CHECK约束语法", "description": "检查约束关键字错误", "ability_dim": "SQL编程与优化", "user_answer": "VALID"}})
            assert r1.status_code == 200
            r2 = await c.get("/api/learning/profile")
            weak = r2.json().get("weak_points", {})
            assert "CHECK约束语法" in weak
            results.append(("Weak Points", "PASS")); print(f"PASS: {list(weak.keys())}")
        except Exception as e:
            results.append(("Weak Points", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 6: Error patterns
        print("\n=== 6. Error Patterns ===")
        try:
            r = await c.get("/api/learning/error-patterns")
            assert r.status_code == 200
            pats = r.json()
            results.append(("Error Patterns", "PASS")); print(f"PASS: {len(pats)} patterns")
            for p in pats[:3]:
                print(f"  - {p['category']}: {p['occurrence_count']}x")
        except Exception as e:
            results.append(("Error Patterns", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 7: Dashboard
        print("\n=== 7. Dashboard ===")
        try:
            r = await c.get("/api/learning/dashboard")
            d = r.json()
            assert "profile" in d and "timeline" in d
            results.append(("Dashboard", "PASS")); print(f"PASS: timeline={len(d['timeline'])}, history={len(d['ability_history'])}")
        except Exception as e:
            results.append(("Dashboard", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 8: Recommendations (LLM)
        print("\n=== 8. Recommendations (LLM) ===")
        try:
            r = await c.get("/api/learning/recommendations", params={"refresh": "true"})
            assert r.status_code == 200
            recs = r.json()
            results.append(("Recommendations", "PASS")); print(f"PASS: {len(recs)} recs")
            for rec in recs[:3]:
                print(f"  - [{rec['rec_type']}] {rec['title']} P{rec['priority']}")
        except Exception as e:
            results.append(("Recommendations", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 9: Ability history
        print("\n=== 9. Ability History ===")
        try:
            r = await c.get("/api/learning/ability-history")
            h = r.json()
            results.append(("Ability History", "PASS")); print(f"PASS: {len(h)} snapshots")
            if h:
                print(f"  latest: {h[-1]['trigger_event']}")
        except Exception as e:
            results.append(("Ability History", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 10: Timeline
        print("\n=== 10. Timeline ===")
        try:
            r = await c.get("/api/learning/timeline", params={"days": 7})
            evts = r.json().get("events", [])
            results.append(("Timeline", "PASS")); print(f"PASS: {len(evts)} events")
            for e in evts[:5]:
                print(f"  - {e['event_type']} lv={e.get('level')} @ {e.get('created_at','')[:16]}")
        except Exception as e:
            results.append(("Timeline", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 11: Second challenge pass
        print("\n=== 11. Second Challenge Pass ===")
        try:
            r1 = await c.post("/api/learning/events", json={"event_type": "challenge_pass", "level": 2, "detail": {"attempts": 2, "duration_seconds": 300}})
            assert r1.status_code == 200
            r2 = await c.get("/api/learning/profile")
            scores = r2.json()["ability_scores"]
            assert scores.get("基础环境搭建", 10) > 10
            results.append(("Second Boost", "PASS")); print(f"PASS: 基础环境搭建={scores['基础环境搭建']}")
        except Exception as e:
            results.append(("Second Boost", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 12: Badges
        print("\n=== 12. Badges ===")
        try:
            r = await c.get("/api/learning/profile")
            badges = r.json().get("badges", {})
            assert "first_clear" in badges and "double_clear" in badges
            results.append(("Badges", "PASS")); print(f"PASS: {list(badges.keys())}")
        except Exception as e:
            results.append(("Badges", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 13: Challenge progress
        print("\n=== 13. Challenge Progress ===")
        try:
            r = await c.get("/api/learning/profile")
            prog = r.json().get("challenge_progress", {})
            assert prog.get("1", {}).get("status") == "passed"
            assert prog.get("2", {}).get("status") == "passed"
            results.append(("Challenge Progress", "PASS")); print(f"PASS: levels={list(prog.keys())}")
        except Exception as e:
            results.append(("Challenge Progress", f"FAIL: {e}")); print(f"FAIL: {e}")

        # 14: RAG Chat with profile
        print("\n=== 14. RAG Chat with Profile ===")
        try:
            r = await c.post("/api/chat/ask", json={"message": "openGauss中外键约束怎么写？"})
            assert r.status_code == 200
            answer = r.json().get("answer", "")
            assert len(answer) > 10
            results.append(("RAG Chat", "PASS")); print(f"PASS: {len(answer)} chars")
        except Exception as e:
            results.append(("RAG Chat", f"FAIL: {e}")); print(f"FAIL: {e}")

    # Frontend test with Playwright
    print("\n=== 15. Frontend Pages ===")
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1400, "height": 900})

            # Profile page
            await page.goto("http://localhost:3000/profile", wait_until="networkidle", timeout=15000)
            content = await page.content()
            sections = ["能力雷达图", "学习统计", "薄弱环节", "智能推荐", "学习时间线"]
            found = [s for s in sections if s in content]
            print(f"  Profile: {len(found)}/{len(sections)} sections ({', '.join(found)})")

            # Challenge page
            await page.goto("http://localhost:3000/challenge", wait_until="networkidle", timeout=15000)
            content = await page.content()
            has_challenge = "选择关卡" in content and "ER图复位" in content
            print(f"  Challenge: {'✓' if has_challenge else '✗'}")

            # Chat page
            await page.goto("http://localhost:3000/", wait_until="networkidle", timeout=15000)
            content = await page.content()
            has_chat = "OpenGauss" in content
            print(f"  Chat: {'✓' if has_chat else '✗'}")

            await browser.close()
            results.append(("Frontend", "PASS"))
    except Exception as e:
        results.append(("Frontend", f"FAIL: {e}")); print(f"  FAIL: {e}")

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    p = sum(1 for _, r in results if r == "PASS")
    for name, r in results:
        icon = "✓" if r == "PASS" else "✗"
        print(f"  {icon} {name}: {r}")
    print(f"\n{p}/{len(results)} passed")

asyncio.run(main())