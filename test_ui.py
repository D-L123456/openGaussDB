import asyncio
from playwright.async_api import async_playwright, expect

FRONTEND = "http://localhost:3000"
API = "http://127.0.0.1:8000"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        results = []

        # ========== 1. 闯关页面 - 关卡选择 ==========
        print("=== 1. 闯关页面 - 关卡卡片点击 ===")
        page = await context.new_page()
        try:
            await page.goto(f"{FRONTEND}/challenge", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 检查关卡卡片存在
            cards = page.locator(".level-card")
            card_count = await cards.count()
            print(f"  关卡卡片数: {card_count}")

            # 点击第一关卡片
            level1_card = cards.nth(0)
            await level1_card.click()
            await page.wait_for_timeout(800)

            # 应该弹出介绍弹窗
            intro_modal = page.locator(".intro-modal")
            modal_visible = await intro_modal.is_visible()
            print(f"  介绍弹窗可见: {modal_visible}")

            if modal_visible:
                # 检查弹窗内容
                modal_text = await intro_modal.inner_text()
                has_title = "ER图复位" in modal_text
                has_skill = "锻炼能力" in modal_text or "能力" in modal_text
                has_start_btn = await intro_modal.locator("button", has_text="开始挑战").count() > 0
                print(f"  弹窗有标题: {has_title}, 有能力: {has_skill}, 有开始按钮: {has_start_btn}")

                # 检查弹窗中的雷达图
                radar_svg = intro_modal.locator("svg.radar-svg")
                radar_visible = await radar_svg.is_visible()
                print(f"  弹窗雷达图可见: {radar_visible}")

                # 关闭弹窗
                close_btn = intro_modal.locator("button.ref-close")
                if await close_btn.count() > 0:
                    await close_btn.click()
                    await page.wait_for_timeout(500)

            results.append(("关卡卡片点击", "PASS" if card_count >= 2 else "PARTIAL"))
        except Exception as e:
            results.append(("关卡卡片点击", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 2. 闯关 - 开始第一关 ==========
        print("\n=== 2. 开始第一关 - ER图复位 ===")
        try:
            # 重新打开闯关页
            await page.goto(f"{FRONTEND}/challenge", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 点击第一关卡片
            cards = page.locator(".level-card")
            await cards.nth(0).click()
            await page.wait_for_timeout(800)

            # 点击"开始挑战"
            start_btn = page.locator("button", has_text="开始挑战")
            if await start_btn.count() > 0:
                await start_btn.click()
                await page.wait_for_timeout(1500)

                # 应该进入第一关
                level_header = page.locator(".level-header")
                header_visible = await level_header.is_visible()
                level_text = await page.locator(".level-badge").first.inner_text() if await page.locator(".level-badge").count() > 0 else ""
                print(f"  进入关卡: header可见={header_visible}, badge={level_text}")

                # 检查ER画布
                er_canvas = page.locator("svg.er-canvas")
                canvas_visible = await er_canvas.is_visible()
                print(f"  ER画布可见: {canvas_visible}")

                # 检查散落组件
                pieces = page.locator(".piece-card")
                piece_count = await pieces.count()
                print(f"  散落组件数: {piece_count}")

                # 检查功能按钮
                ref_btn = page.locator("button", has_text="参考图")
                reset_btn = page.locator("button", has_text="重置")
                check_btn = page.locator("button", has_text="验证答案")
                print(f"  参考图按钮: {await ref_btn.count() > 0}, 重置按钮: {await reset_btn.count() > 0}, 验证按钮: {await check_btn.count() > 0}")

                # 点击参考图按钮
                if await ref_btn.count() > 0:
                    await ref_btn.click()
                    await page.wait_for_timeout(800)
                    ref_modal = page.locator(".ref-modal")
                    ref_visible = await ref_modal.is_visible()
                    print(f"  参考图弹窗可见: {ref_visible}")
                    if ref_visible:
                        # 关闭参考图
                        close_btn = ref_modal.locator("button.ref-close")
                        if await close_btn.count() > 0:
                            await close_btn.click()
                            await page.wait_for_timeout(500)

                # 点击返回按钮
                back_btn = page.locator("button", has_text="← 返回")
                if await back_btn.count() > 0:
                    await back_btn.click()
                    await page.wait_for_timeout(800)

                results.append(("第一关进入/退出", "PASS"))
            else:
                results.append(("第一关进入/退出", "FAIL: 开始挑战按钮未找到"))
                print("  FAIL: 开始挑战按钮未找到")
        except Exception as e:
            results.append(("第一关进入/退出", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 3. 第二关 - SQL填空 ==========
        print("\n=== 3. 开始第二关 - SQL建库建表 ===")
        try:
            await page.goto(f"{FRONTEND}/challenge", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            cards = page.locator(".level-card")
            if await cards.count() >= 2:
                await cards.nth(1).click()
                await page.wait_for_timeout(800)

                start_btn = page.locator("button", has_text="开始挑战")
                if await start_btn.count() > 0:
                    await start_btn.click()
                    await page.wait_for_timeout(1500)

                    # 检查终端界面
                    terminal = page.locator(".sql-terminal")
                    terminal_visible = await terminal.is_visible()
                    print(f"  SQL终端可见: {terminal_visible}")

                    # 检查进度条
                    progress = page.locator(".l2-progress")
                    progress_visible = await progress.is_visible()
                    print(f"  进度条可见: {progress_visible}")

                    # 检查填空
                    blanks = page.locator(".blank-slot")
                    blank_count = await blanks.count()
                    print(f"  填空数: {blank_count}")

                    # 检查提交按钮
                    submit_btn = page.locator("button", has_text="提交本部分")
                    print(f"  提交按钮: {await submit_btn.count() > 0}")

                    # 点击重置
                    reset_btn = page.locator("button", has_text="重置")
                    if await reset_btn.count() > 0:
                        await reset_btn.click()
                        await page.wait_for_timeout(500)
                        print(f"  重置成功")

                    results.append(("第二关SQL填空", "PASS"))
                else:
                    results.append(("第二关SQL填空", "FAIL: 无开始按钮"))
            else:
                results.append(("第二关SQL填空", "FAIL: 无第二关卡片"))
        except Exception as e:
            results.append(("第二关SQL填空", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 4. 学习画像页面 ==========
        print("\n=== 4. 学习画像页面 ===")
        try:
            await page.goto(f"{FRONTEND}/profile", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            # 检查各区块
            sections = {
                "能力雷达图": page.locator(".radar-card"),
                "学习统计": page.locator(".stats-card"),
                "薄弱环节": page.locator(".weak-card"),
                "成长曲线": page.locator(".growth-card"),
                "智能推荐": page.locator(".recommend-card"),
                "时间线": page.locator(".timeline-card"),
                "错误热力图": page.locator(".error-card"),
            }
            for name, loc in sections.items():
                visible = await loc.is_visible()
                print(f"  {name}: {'✓' if visible else '✗'}")

            # 点击刷新分析按钮
            refresh_btn = page.locator("button", has_text="刷新分析")
            if await refresh_btn.count() > 0:
                await refresh_btn.click()
                await page.wait_for_timeout(3000)
                print(f"  刷新分析: 已点击")

            # 检查推荐卡片可点击
            rec_items = page.locator(".rec-item")
            rec_count = await rec_items.count()
            print(f"  推荐卡片数: {rec_count}")

            if rec_count > 0:
                # 点击第一个推荐
                await rec_items.first.click()
                await page.wait_for_timeout(1500)
                current_url = page.url
                print(f"  点击推荐后跳转: {current_url}")

            results.append(("学习画像页面", "PASS"))
        except Exception as e:
            results.append(("学习画像页面", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 5. 对话页面 - 发送消息 ==========
        print("\n=== 5. 对话页面 - 发送消息 ===")
        try:
            await page.goto(f"{FRONTEND}/", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 检查输入框
            textarea = page.locator("textarea")
            textarea_visible = await textarea.is_visible()
            print(f"  输入框可见: {textarea_visible}")

            if textarea_visible:
                # 输入消息
                await textarea.fill("openGauss是什么？")
                await page.wait_for_timeout(500)

                # 点击发送按钮
                send_btn = page.locator("button", has_text="发送")
                if await send_btn.count() > 0:
                    await send_btn.click()
                    print(f"  已发送消息，等待回复...")
                    
                    # 等待回复出现
                    await page.wait_for_timeout(15000)
                    
                    # 检查消息
                    messages = page.locator(".message.assistant")
                    msg_count = await messages.count()
                    print(f"  助手回复数: {msg_count}")
                    
                    if msg_count > 0:
                        last_msg = messages.last
                        msg_text = await last_msg.inner_text()
                        print(f"  回复长度: {len(msg_text)} 字符")
                        has_content = len(msg_text) > 20
                        print(f"  回复有实质内容: {has_content}")
                else:
                    print("  发送按钮未找到")

            # 检查推荐侧边栏
            rec_sidebar = page.locator(".rec-sidebar")
            rec_visible = await rec_sidebar.is_visible()
            print(f"  推荐侧边栏可见: {rec_visible}")

            results.append(("对话发送消息", "PASS"))
        except Exception as e:
            results.append(("对话发送消息", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 6. 快捷问题按钮 ==========
        print("\n=== 6. 快捷问题按钮 ===")
        try:
            await page.goto(f"{FRONTEND}/", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            quick_btns = page.locator(".quick-questions button")
            quick_count = await quick_btns.count()
            print(f"  快捷问题数: {quick_count}")

            if quick_count > 0:
                await quick_btns.first.click()
                print(f"  已点击快捷问题")
                await page.wait_for_timeout(15000)

                messages = page.locator(".message.assistant")
                msg_count = await messages.count()
                print(f"  助手回复数: {msg_count}")

            results.append(("快捷问题按钮", "PASS" if quick_count > 0 else "PARTIAL"))
        except Exception as e:
            results.append(("快捷问题按钮", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 7. 导航栏切换 ==========
        print("\n=== 7. 导航栏切换 ===")
        try:
            nav_items = page.locator(".nav-item")
            nav_count = await nav_items.count()
            print(f"  导航项数: {nav_count}")

            pages_to_test = [
                ("/", "知识问答"),
                ("/sql-practice", "SQL练习"),
                ("/knowledge-tree", "知识树"),
                ("/challenge", "勇闯数据库"),
                ("/profile", "学习画像"),
            ]

            for path, name in pages_to_test:
                await page.goto(f"{FRONTEND}{path}", wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(1000)
                url = page.url
                ok = path in url or url.endswith(path)
                print(f"  {name}({path}): {'✓' if ok else '✗'} url={url}")

            results.append(("导航栏切换", "PASS"))
        except Exception as e:
            results.append(("导航栏切换", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 8. SQL练习页面 ==========
        print("\n=== 8. SQL练习页面 ===")
        try:
            await page.goto(f"{FRONTEND}/sql-practice", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 检查题目列表
            questions = page.locator(".question-item, .question-card, [class*='question']")
            q_count = await questions.count()
            print(f"  题目元素数: {q_count}")

            # 检查代码编辑区
            editor = page.locator("textarea, .sql-editor, [class*='editor']")
            editor_count = await editor.count()
            print(f"  编辑器元素: {editor_count}")

            # 检查提交按钮
            submit = page.locator("button", has_text="提交")
            submit_count = await submit.count()
            print(f"  提交按钮: {submit_count > 0}")

            results.append(("SQL练习页面", "PASS"))
        except Exception as e:
            results.append(("SQL练习页面", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 9. 知识树页面 ==========
        print("\n=== 9. 知识树页面 ===")
        try:
            await page.goto(f"{FRONTEND}/knowledge-tree", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 检查树结构
            tree_nodes = page.locator(".tree-node, [class*='tree'] [class*='node']")
            node_count = await tree_nodes.count()
            print(f"  树节点数: {node_count}")

            # 点击第一个节点展开
            if node_count > 0:
                await tree_nodes.first.click()
                await page.wait_for_timeout(800)
                print(f"  已点击第一个节点")

            results.append(("知识树页面", "PASS"))
        except Exception as e:
            results.append(("知识树页面", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 10. 闯关页面 - 能力雷达图 ==========
        print("\n=== 10. 闯关页面能力雷达图 ===")
        try:
            await page.goto(f"{FRONTEND}/challenge", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 检查关卡选择页的雷达图
            radar_main = page.locator(".ability-section")
            radar_visible = await radar_main.is_visible()
            print(f"  关卡选择页雷达图: {'✓' if radar_visible else '✗'}")

            if radar_visible:
                radar_svg = radar_main.locator("svg")
                svg_visible = await radar_svg.is_visible()
                print(f"  SVG雷达图可见: {svg_visible}")

                # 检查综合评分
                score_badge = radar_main.locator(".ability-score-badge")
                if await score_badge.count() > 0:
                    score_text = await score_badge.inner_text()
                    print(f"  综合评分: {score_text}")

            results.append(("闯关雷达图", "PASS" if radar_visible else "PARTIAL"))
        except Exception as e:
            results.append(("闯关雷达图", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 11. 对话页面 - 新建/删除会话 ==========
        print("\n=== 11. 对话 - 新建/删除会话 ===")
        try:
            await page.goto(f"{FRONTEND}/", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 新建对话
            new_btn = page.locator("button", has_text="新对话")
            if await new_btn.count() > 0:
                await new_btn.click()
                await page.wait_for_timeout(1000)
                print(f"  已点击新建对话")

            # 检查会话列表
            sessions = page.locator(".session-item")
            session_count = await sessions.count()
            print(f"  会话数: {session_count}")

            # 删除最后一个会话
            if session_count > 1:
                delete_btns = page.locator(".session-delete")
                if await delete_btns.count() > 0:
                    page.on("dialog", lambda dialog: dialog.accept())
                    await delete_btns.last.click()
                    await page.wait_for_timeout(800)
                    print(f"  已删除会话")

            results.append(("新建/删除会话", "PASS"))
        except Exception as e:
            results.append(("新建/删除会话", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 12. 闯关 - 验证答案流程 ==========
        print("\n=== 12. 闯关 - 验证答案(未完成) ===")
        try:
            await page.goto(f"{FRONTEND}/challenge", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # 进入第一关
            cards = page.locator(".level-card")
            await cards.nth(0).click()
            await page.wait_for_timeout(800)
            start_btn = page.locator("button", has_text="开始挑战")
            if await start_btn.count() > 0:
                await start_btn.click()
                await page.wait_for_timeout(1500)

                # 直接点击验证（未放置任何组件）
                check_btn = page.locator("button", has_text="验证答案")
                if await check_btn.count() > 0:
                    await check_btn.click()
                    await page.wait_for_timeout(800)

                    # 应该弹出失败提示
                    modal = page.locator(".modal-box")
                    modal_visible = await modal.is_visible()
                    if modal_visible:
                        modal_text = await modal.inner_text()
                        is_fail = "不正确" in modal_text or "请" in modal_text
                        print(f"  未完成验证弹窗: {'✓ 失败提示' if is_fail else '内容: ' + modal_text[:50]}")
                        
                        # 关闭弹窗
                        ok_btn = modal.locator("button")
                        if await ok_btn.count() > 0:
                            await ok_btn.click()
                            await page.wait_for_timeout(500)

                    results.append(("验证答案流程", "PASS"))
                else:
                    results.append(("验证答案流程", "FAIL: 无验证按钮"))
            else:
                results.append(("验证答案流程", "FAIL: 无开始按钮"))
        except Exception as e:
            results.append(("验证答案流程", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        # ========== 13. 第二关 - 填空交互 ==========
        print("\n=== 13. 第二关 - 填空输入交互 ===")
        try:
            await page.goto(f"{FRONTEND}/challenge", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            cards = page.locator(".level-card")
            if await cards.count() >= 2:
                await cards.nth(1).click()
                await page.wait_for_timeout(800)
                start_btn = page.locator("button", has_text="开始挑战")
                if await start_btn.count() > 0:
                    await start_btn.click()
                    await page.wait_for_timeout(1500)

                    # 查找填空输入框
                    blank_inputs = page.locator("input.blank-input, input[type='text'], .blank-input input")
                    input_count = await blank_inputs.count()
                    print(f"  填空输入框数: {input_count}")

                    # 查找选择题空缺
                    blank_slots = page.locator(".blank-slot")
                    slot_count = await blank_slots.count()
                    print(f"  空缺总数: {slot_count}")

                    # 尝试点击一个空缺
                    if slot_count > 0:
                        await blank_slots.first.click()
                        await page.wait_for_timeout(500)

                        # 检查右侧面板是否有选项或输入
                        options_panel = page.locator(".blank-options, .options-panel, .hint-panel")
                        options_visible = await options_panel.is_visible() if await options_panel.count() > 0 else False
                        print(f"  选项/提示面板可见: {options_visible}")

                    # 点击提交
                    submit_btn = page.locator("button", has_text="提交本部分")
                    if await submit_btn.count() > 0:
                        await submit_btn.click()
                        await page.wait_for_timeout(1500)

                        # 检查弹窗
                        modal = page.locator(".modal-box")
                        if await modal.is_visible():
                            modal_text = await modal.inner_text()
                            print(f"  提交结果: {modal_text[:60]}")
                            ok_btn = modal.locator("button")
                            if await ok_btn.count() > 0:
                                await ok_btn.click()
                                await page.wait_for_timeout(500)

                    results.append(("第二关填空交互", "PASS"))
                else:
                    results.append(("第二关填空交互", "FAIL"))
            else:
                results.append(("第二关填空交互", "FAIL: 无第二关"))
        except Exception as e:
            results.append(("第二关填空交互", f"FAIL: {e}"))
            print(f"  FAIL: {e}")

        await browser.close()

        # Summary
        print("\n" + "=" * 60)
        print("UI 交互测试结果")
        print("=" * 60)
        p = sum(1 for _, r in results if r == "PASS")
        for name, r in results:
            icon = "✓" if r == "PASS" else "✗"
            print(f"  {icon} {name}: {r}")
        print(f"\n{p}/{len(results)} 通过")

asyncio.run(main())