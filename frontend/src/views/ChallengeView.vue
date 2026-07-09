<template>
  <div class="challenge-view">
    <div class="header">⚔️ 勇闯数据库</div>
    <div class="content-area">
      <div v-if="currentLevel === 0" class="level-select">
        <h2 class="level-title">选择关卡</h2>
        <div class="level-grid">
          <div class="level-card" :class="{ active: !completedLevels.has(1), completed: completedLevels.has(1) }" @click="showLevelIntro(1)">
            <div class="level-num">第一关</div>
            <div class="level-name">ER图复位</div>
            <div class="level-desc">根据ER关系图，将拆散的组件拖拽回正确位置</div>
            <div class="level-difficulty">{{ completedLevels.has(1) ? '✅ 已通关' : '难度：⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(2), completed: completedLevels.has(2) }" @click="showLevelIntro(2)">
            <div class="level-num">第二关</div>
            <div class="level-name">SQL建库建表</div>
            <div class="level-desc">补全openGauss数据库创建与表设计的SQL命令</div>
            <div class="level-difficulty">{{ completedLevels.has(2) ? '✅ 已通关' : '难度：⭐⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(3), completed: completedLevels.has(3) }" @click="showLevelIntro(3)">
            <div class="level-num">第三关</div>
            <div class="level-name">数据录入与修改</div>
            <div class="level-desc">仿写INSERT和UPDATE语句，完成银行业务数据的录入与维护</div>
            <div class="level-difficulty">{{ completedLevels.has(3) ? '✅ 已通关' : '难度：⭐⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(4), completed: completedLevels.has(4) }" @click="showLevelIntro(4)">
            <div class="level-num">第四关</div>
            <div class="level-name">视图与存储过程</div>
            <div class="level-desc">拖拽打乱的SQL代码块，拼出完整的视图和存储过程</div>
            <div class="level-difficulty">{{ completedLevels.has(4) ? '✅ 已通关' : '难度：⭐⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(5), completed: completedLevels.has(5) }" @click="showLevelIntro(5)">
            <div class="level-num">第五关</div>
            <div class="level-name">触发器与事务</div>
            <div class="level-desc">在流程图中连线，走通触发器逻辑和事务流程</div>
            <div class="level-difficulty">{{ completedLevels.has(5) ? '✅ 已通关' : '难度：⭐⭐⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(6), completed: completedLevels.has(6) }" @click="showLevelIntro(6)">
            <div class="level-num">第六关</div>
            <div class="level-name">性能调优</div>
            <div class="level-desc">阅读慢查询场景，手动编写优化SQL语句提升性能</div>
            <div class="level-difficulty">{{ completedLevels.has(6) ? '✅ 已通关' : '难度：⭐⭐⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(7), completed: completedLevels.has(7) }" @click="showLevelIntro(7)">
            <div class="level-num">第七关</div>
            <div class="level-name">数据库安全与权限</div>
            <div class="level-desc">补全用户角色创建、权限授予与回收的SQL命令</div>
            <div class="level-difficulty">{{ completedLevels.has(7) ? '✅ 已通关' : '难度：⭐⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(8), completed: completedLevels.has(8) }" @click="showLevelIntro(8)">
            <div class="level-num">第八关</div>
            <div class="level-name">备份与恢复</div>
            <div class="level-desc">拖拽排列gs_dump和gs_restore命令的正确执行步骤</div>
            <div class="level-difficulty">{{ completedLevels.has(8) ? '✅ 已通关' : '难度：⭐⭐⭐' }}</div>
          </div>
          <div class="level-card" :class="{ active: !completedLevels.has(9), completed: completedLevels.has(9) }" @click="showLevelIntro(9)">
            <div class="level-num">第九关</div>
            <div class="level-name">综合实战：Bug猎人</div>
            <div class="level-desc">找出SQL代码中的Bug并修正，考验综合能力</div>
            <div class="level-difficulty">{{ completedLevels.has(9) ? '✅ 已通关' : '难度：⭐⭐⭐⭐⭐' }}</div>
          </div>
        </div>

        <div class="ability-section">
          <div class="ability-header">
            <span class="ability-title">能力画像</span>
            <span class="ability-score-badge">综合评分：{{ abilityScore }} / 100</span>
          </div>
          <svg viewBox="0 0 300 300" class="radar-svg-main">
            <polygon v-for="r in [80, 60, 40, 20]" :key="r" :points="radarGrid(r)" fill="none" stroke="#e2e8f0" stroke-width="1"/>
            <line v-for="i in 8" :key="'l'+i" :x1="150" :y1="150" :x2="radarPoint(i, 80).x" :y2="radarPoint(i, 80).y" stroke="#e2e8f0" stroke-width="1"/>
            <polygon :points="radarArea()" fill="rgba(59,130,246,0.2)" stroke="#3b82f6" stroke-width="2"/>
            <circle v-for="i in 8" :key="'d'+i" :cx="radarPoint(i, abilities[i-1] * 0.8).x" :cy="radarPoint(i, abilities[i-1] * 0.8).y" r="4" fill="#3b82f6"/>
            <text v-for="(dim, i) in abilityDims" :key="'t'+i" :x="radarPoint(i+1, 95).x" :y="radarPoint(i+1, 95).y" text-anchor="middle" fill="#374151" font-size="10" font-weight="500">{{ dim }}</text>
          </svg>
        </div>

        <div v-if="showIntroModal" class="modal-overlay" @click.self="showIntroModal=false">
          <div class="intro-modal">
            <div class="intro-modal-header">
              <span>{{ levelIntros[introLevel]?.title }}</span>
              <button class="ref-close" @click="showIntroModal=false">×</button>
            </div>
            <div class="intro-body">
              <div class="intro-left">
                <div class="intro-section">
                  <div class="intro-label">关卡简介</div>
                  <div class="intro-text">{{ levelIntros[introLevel]?.desc }}</div>
                </div>
                <div class="intro-section">
                  <div class="intro-label">锻炼能力</div>
                  <div class="intro-skills">
                    <span v-for="s in levelIntros[introLevel]?.skills" :key="s" class="intro-skill-tag">{{ s }}</span>
                  </div>
                </div>
                <div class="intro-section">
                  <div class="intro-label">当前能力值</div>
                  <div class="intro-score">{{ abilityScore }} / 100</div>
                </div>
                <button class="btn btn-primary intro-start-btn" @click="startLevel(introLevel)">开始挑战</button>
              </div>
              <div class="intro-right">
                <svg viewBox="0 0 300 300" class="radar-svg">
                  <polygon v-for="r in [80, 60, 40, 20]" :key="r" :points="radarGrid(r)" fill="none" stroke="#e2e8f0" stroke-width="1"/>
                  <line v-for="i in 8" :key="'l'+i" :x1="150" :y1="150" :x2="radarPoint(i, 80).x" :y2="radarPoint(i, 80).y" stroke="#e2e8f0" stroke-width="1"/>
                  <polygon :points="radarArea()" fill="rgba(59,130,246,0.2)" stroke="#3b82f6" stroke-width="2"/>
                  <circle v-for="i in 8" :key="'d'+i" :cx="radarPoint(i, abilities[i-1] * 0.8).x" :cy="radarPoint(i, abilities[i-1] * 0.8).y" r="4" fill="#3b82f6"/>
                  <text v-for="(dim, i) in abilityDims" :key="'t'+i" :x="radarPoint(i+1, 95).x" :y="radarPoint(i+1, 95).y" text-anchor="middle" fill="#374151" font-size="10" font-weight="500">{{ dim }}</text>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 1" class="level-1">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第一关</span>
            <span class="level-label">ER图复位</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="showRef = true">📋 参考图</button>
            <button class="btn" @click="resetLevel1">重置</button>
            <button class="btn btn-primary" @click="checkLevel1">验证答案</button>
          </div>
        </div>
        <div class="level-hint"><strong>任务说明：</strong>ER图中有5个组件被拆散，请根据参考图中的关系，将它们拖拽回左侧画布的虚线位置。</div>

        <div class="er-workspace">
          <div class="er-canvas-wrapper">
            <svg class="er-canvas" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
              <g class="fixed-lines">
                <line x1="200" y1="350" x2="300" y2="350" stroke="#94a3b8" stroke-width="1.5"/>
                <line x1="380" y1="350" x2="500" y2="350" stroke="#94a3b8" stroke-width="1.5"/>
                <text x="250" y="338" text-anchor="middle" fill="#3b82f6" font-size="13" font-weight="600">1</text>
                <text x="440" y="338" text-anchor="middle" fill="#3b82f6" font-size="13" font-weight="600">N</text>
                <line x1="600" y1="350" x2="645" y2="350" stroke="#94a3b8" stroke-width="1.5"/>
                <line x1="725" y1="350" x2="820" y2="350" stroke="#94a3b8" stroke-width="1.5"/>
                <text x="622" y="338" text-anchor="middle" fill="#3b82f6" font-size="13" font-weight="600">N</text>
                <text x="772" y="338" text-anchor="middle" fill="#3b82f6" font-size="13" font-weight="600">1</text>
                <line x1="550" y1="370" x2="550" y2="485" stroke="#94a3b8" stroke-width="1.5"/>
                <line x1="550" y1="535" x2="550" y2="560" stroke="#94a3b8" stroke-width="1.5"/>
                <text x="570" y="430" fill="#3b82f6" font-size="13" font-weight="600">1</text>
                <text x="570" y="555" fill="#3b82f6" font-size="13" font-weight="600">N</text>
                <line v-for="l in fixedAttrLines" :key="l.id" :x1="l.x1" :y1="l.y1" :x2="l.x2" :y2="l.y2" stroke="#94a3b8" stroke-width="1"/>
              </g>
              <g v-for="item in fixedItems" :key="item.id" :transform="`translate(${item.x},${item.y})`">
                <rect v-if="item.shape==='rect'" x="-50" y="-20" width="100" height="40" rx="3" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
                <text v-if="item.shape==='rect'" x="0" y="6" text-anchor="middle" fill="#1e293b" font-size="14" font-weight="600">{{ item.label }}</text>
                <ellipse v-if="item.shape==='ellipse'" cx="0" cy="0" :rx="item.rx||50" ry="17" fill="#d1fae5" stroke="#10b981" stroke-width="1.5"/>
                <text v-if="item.shape==='ellipse'" x="0" y="5" text-anchor="middle" :fill="item.pk?'#dc2626':'#374151'" :font-weight="item.pk?700:400" font-size="11" :text-decoration="item.pk?'underline':'none'">{{ item.label }}</text>
                <polygon v-if="item.shape==='diamond'" points="0,-25 40,0 0,25 -40,0" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
                <text v-if="item.shape==='diamond'" x="0" y="5" text-anchor="middle" fill="#92400e" font-size="12" font-weight="600">{{ item.label }}</text>
              </g>
              <g v-for="slot in removableSlots" :key="slot.id">
                <g v-if="slot.matched" :transform="`translate(${slot.x},${slot.y})`">
                  <rect v-if="slot.shape==='rect'" x="-50" y="-20" width="100" height="40" rx="3" :fill="slot.wrong?'#fef2f2':'#dbeafe'" :stroke="slot.wrong?'#ef4444':'#3b82f6'" stroke-width="2"/>
                  <text v-if="slot.shape==='rect'" x="0" y="6" text-anchor="middle" fill="#1e293b" font-size="14" font-weight="600">{{ slot.matchLabel }}</text>
                  <ellipse v-if="slot.shape==='ellipse'" cx="0" cy="0" :rx="slot.rx||50" ry="17" :fill="slot.wrong?'#fef2f2':'#d1fae5'" :stroke="slot.wrong?'#ef4444':'#10b981'" stroke-width="1.5"/>
                  <text v-if="slot.shape==='ellipse'" x="0" y="5" text-anchor="middle" :fill="slot.pk?'#dc2626':'#374151'" :font-weight="slot.pk?700:400" font-size="11" :text-decoration="slot.pk?'underline':'none'">{{ slot.matchLabel }}</text>
                  <polygon v-if="slot.shape==='diamond'" points="0,-25 40,0 0,25 -40,0" :fill="slot.wrong?'#fef2f2':'#fef3c7'" :stroke="slot.wrong?'#ef4444':'#f59e0b'" stroke-width="2"/>
                  <text v-if="slot.shape==='diamond'" x="0" y="5" text-anchor="middle" fill="#92400e" font-size="12" font-weight="600">{{ slot.matchLabel }}</text>
                </g>
                <g v-else :transform="`translate(${slot.x},${slot.y})`" class="slot-area" @dragover.prevent @drop="onDropSlot($event, slot)">
                  <rect v-if="slot.shape==='rect'" x="-50" y="-20" width="100" height="40" rx="3" fill="rgba(255,255,255,0.4)" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="6,4"/>
                  <ellipse v-if="slot.shape==='ellipse'" cx="0" cy="0" :rx="slot.rx||50" ry="17" fill="rgba(255,255,255,0.4)" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="6,4"/>
                  <polygon v-if="slot.shape==='diamond'" points="0,-25 40,0 0,25 -40,0" fill="rgba(255,255,255,0.4)" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="6,4"/>
                  <text x="0" y="4" text-anchor="middle" fill="#94a3b8" font-size="10">?</text>
                </g>
              </g>
            </svg>
          </div>
          <div class="er-pieces">
            <div class="pieces-header">散落组件（5个）</div>
            <div class="pieces-list">
              <div v-for="piece in pieces" :key="piece.id" class="piece-card" :class="[{ used: piece.used }, piece.shape]" :draggable="!piece.used" @dragstart="onDragStart($event, piece)">
                <div class="piece-shape-icon">
                  <span v-if="piece.shape==='rect'">▭</span>
                  <span v-else-if="piece.shape==='ellipse'">◯</span>
                  <span v-else>◇</span>
                </div>
                <div class="piece-info">
                  <div class="piece-label">{{ piece.label }}</div>
                  <div class="piece-type">{{ piece.shape==='rect'?'实体':piece.shape==='diamond'?'关系':'属性' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showRef" class="modal-overlay" @click.self="showRef=false">
          <div class="ref-modal">
            <div class="ref-modal-header"><span>📋 参考图 — 逻辑模型</span><button class="ref-close" @click="showRef=false">×</button></div>
            <svg viewBox="0 0 960 560" xmlns="http://www.w3.org/2000/svg" class="ref-svg">
              <defs><marker id="ra" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#94a3b8"/></marker></defs>
              <line x1="200" y1="180" x2="280" y2="180" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#ra)"/><text x="240" y="170" text-anchor="middle" fill="#64748b" font-size="12">使用</text><text x="240" y="198" text-anchor="middle" fill="#94a3b8" font-size="10">1:N</text>
              <line x1="620" y1="180" x2="700" y2="180" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#ra)"/><text x="660" y="170" text-anchor="middle" fill="#64748b" font-size="12">属于</text><text x="660" y="198" text-anchor="middle" fill="#94a3b8" font-size="10">N:1</text>
              <line x1="450" y1="280" x2="450" y2="350" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#ra)"/><text x="475" y="320" fill="#64748b" font-size="12">记录</text><text x="475" y="336" fill="#94a3b8" font-size="10">1:N</text>
              <g transform="translate(110,180)"><rect x="-90" y="-70" width="180" height="140" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/><rect x="-90" y="-70" width="180" height="28" rx="6" fill="#3b82f6"/><rect x="-90" y="-48" width="180" height="6" fill="#3b82f6"/><text x="0" y="-50" text-anchor="middle" fill="white" font-size="13" font-weight="600">客户</text><text x="-78" y="-28" fill="#dc2626" font-size="11" font-weight="700"># 客户编号 (Serial)</text><text x="-78" y="-12" fill="#374151" font-size="11">客户姓名 (Characters(8))</text><text x="-78" y="4" fill="#374151" font-size="11">手机号码 (Characters(18))</text><text x="-78" y="20" fill="#374151" font-size="11">联系电话 (Characters(20))</text><text x="-78" y="36" fill="#374151" font-size="11">联系地址 (Varchar(50))</text></g>
              <g transform="translate(450,180)"><rect x="-110" y="-100" width="220" height="200" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/><rect x="-110" y="-100" width="220" height="28" rx="6" fill="#3b82f6"/><rect x="-110" y="-78" width="220" height="6" fill="#3b82f6"/><text x="0" y="-80" text-anchor="middle" fill="white" font-size="13" font-weight="600">银行卡</text><text x="-98" y="-58" fill="#dc2626" font-size="11" font-weight="700"># 卡号 (Characters(17))</text><text x="-98" y="-42" fill="#374151" font-size="11">客户编号 (Integer)</text><text x="-98" y="-26" fill="#374151" font-size="11">存款账号 (Integer)</text><text x="-98" y="-10" fill="#374151" font-size="11">币种 (Varchar(10))</text><text x="-98" y="6" fill="#374151" font-size="11">开卡时间 (Timestamp)</text><text x="-98" y="22" fill="#374151" font-size="11">账户余额 (Decimal(18,2))</text><text x="-98" y="38" fill="#374151" font-size="11">信用卡额度 (Decimal(18,2))</text><text x="-98" y="54" fill="#374151" font-size="11">透支额度 (Characters(8))</text><text x="-98" y="70" fill="#374151" font-size="11">是否挂失 (Varchar(5))</text></g>
              <g transform="translate(790,180)"><rect x="-90" y="-54" width="180" height="108" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/><rect x="-90" y="-54" width="180" height="28" rx="6" fill="#3b82f6"/><rect x="-90" y="-32" width="180" height="6" fill="#3b82f6"/><text x="0" y="-34" text-anchor="middle" fill="white" font-size="13" font-weight="600">存款类型</text><text x="-78" y="-12" fill="#dc2626" font-size="11" font-weight="700"># 存款编号 (Serial)</text><text x="-78" y="4" fill="#374151" font-size="11">存款名称 (Varchar(20))</text><text x="-78" y="20" fill="#374151" font-size="11">存款描述 (Varchar(50))</text></g>
              <g transform="translate(450,420)"><rect x="-110" y="-54" width="220" height="124" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/><rect x="-110" y="-54" width="220" height="28" rx="6" fill="#3b82f6"/><rect x="-110" y="-32" width="220" height="6" fill="#3b82f6"/><text x="0" y="-34" text-anchor="middle" fill="white" font-size="13" font-weight="600">交易信息</text><text x="-98" y="-12" fill="#374151" font-size="11">交易类型 (Characters(8))</text><text x="-98" y="4" fill="#374151" font-size="11">卡号 (Characters(17))</text><text x="-98" y="20" fill="#374151" font-size="11">交易时间 (Timestamp)</text><text x="-98" y="36" fill="#374151" font-size="11">交易金额 (Decimal(18,2))</text><text x="-98" y="52" fill="#374151" font-size="11">备注 (Text)</text></g>
            </svg>
          </div>
        </div>

        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? '🎉' : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? '恭喜通关！ER图已正确还原！' : '部分组件位置不正确，请重试' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 2" class="level-2">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第二关</span>
            <span class="level-label">SQL建库建表</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel2">重置</button>
            <button class="btn btn-primary" @click="checkLevel2Part">{{ l2Part < 4 ? '提交本部分' : '验证答案' }}</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>补全SQL命令中的空缺。部分空缺需手动输入，部分可从选项中选择。
          <span style="margin-left:12px">进度：第{{ l2Part }}部分 / 共4部分</span>
        </div>

        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l2Part - 1) / 4 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l2Part > 1, current: l2Part === 1 }">1. 连接与建库</span>
            <span :class="{ done: l2Part > 2, current: l2Part === 2 }">2. 用户与模式</span>
            <span :class="{ done: l2Part > 3, current: l2Part === 3 }">3. 建表</span>
            <span :class="{ current: l2Part === 4 }">4. 表约束</span>
          </div>
        </div>

        <div class="sql-workspace">
          <div class="sql-terminal">
            <div class="terminal-header">
              <span class="terminal-dot red"></span>
              <span class="terminal-dot yellow"></span>
              <span class="terminal-dot green"></span>
              <span class="terminal-title">openGauss Terminal</span>
            </div>
            <div class="terminal-body">
              <div v-for="(line, li) in l2CurrentLines" :key="li" class="sql-line">
                <template v-for="(seg, si) in line" :key="si">
                  <span v-if="seg.type === 'text'" class="sql-text">{{ seg.value }}</span>
                  <template v-else>
                    <span v-if="l2BlankMeta[seg.blankId]?.mode === 'select'" class="sql-blank"
                      :class="{ filled: l2Blanks[seg.blankId]?.filled, correct: l2Blanks[seg.blankId]?.checked && l2Blanks[seg.blankId]?.correct, wrong: l2Blanks[seg.blankId]?.checked && !l2Blanks[seg.blankId]?.correct }"
                      @click="l2ActiveBlank = seg.blankId">
                      {{ l2Blanks[seg.blankId]?.filled ? l2Blanks[seg.blankId]?.value : '____' }}
                    </span>
                    <input v-else class="sql-input"
                      :class="{ correct: l2Blanks[seg.blankId]?.checked && l2Blanks[seg.blankId]?.correct, wrong: l2Blanks[seg.blankId]?.checked && !l2Blanks[seg.blankId]?.correct }"
                      :value="l2Blanks[seg.blankId]?.value || ''"
                      @input="onL2Input(seg.blankId, ($event.target as HTMLInputElement).value)"
                      @focus="l2ActiveBlank = seg.blankId"
                      :placeholder="'输入答案'" />
                  </template>
                </template>
              </div>
            </div>
          </div>

          <div class="sql-options">
            <div class="options-header">答题面板</div>
            <template v-if="l2ActiveBlank !== null && l2BlankMeta[l2ActiveBlank]?.mode === 'select'">
              <div class="options-target">第{{ l2ActiveBlank + 1 }}空 — 选择题</div>
              <div class="options-list">
                <button v-for="opt in l2CurrentOptions" :key="opt" class="option-btn"
                  :class="{ selected: l2Blanks[l2ActiveBlank]?.value === opt }"
                  @click="selectL2Option(opt)">
                  {{ opt }}
                </button>
              </div>
            </template>
            <template v-else-if="l2ActiveBlank !== null && l2BlankMeta[l2ActiveBlank]?.mode === 'input'">
              <div class="options-target">第{{ l2ActiveBlank + 1 }}空 — 填空题</div>
              <div class="options-hint">请在代码中直接输入答案</div>
              <div class="options-hint" style="margin-top:8px;color:#64748b;">提示：{{ l2BlankMeta[l2ActiveBlank]?.hint }}</div>
            </template>
            <div v-else class="options-hint">点击选择题空缺处显示选项</div>
          </div>
        </div>

        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l2Part > 4 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l2Part > 4 ? '恭喜通关！所有SQL命令填写正确！' : '本部分通过！进入下一部分') : '部分空缺填写不正确，请检查红色标记处' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 3" class="level-3">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第三关</span>
            <span class="level-label">数据录入与修改</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel3">重置</button>
            <button class="btn btn-primary" @click="checkLevel3Task">{{ l3Task < 3 ? '提交本题' : '验证全部' }}</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>参照左侧示例SQL，在右侧编辑器中仿写完成对应任务。
          <span style="margin-left:12px">进度：第{{ l3Task }}题 / 共3题</span>
        </div>

        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l3Task - 1) / 3 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l3Task > 1, current: l3Task === 1 }">1. INSERT录入</span>
            <span :class="{ done: l3Task > 2, current: l3Task === 2 }">2. 修改密码</span>
            <span :class="{ current: l3Task === 3 }">3. 挂失银行卡</span>
          </div>
        </div>

        <div class="l3-workspace">
          <div class="l3-ref-panel">
            <div class="l3-panel-header">参考示例</div>
            <div class="l3-ref-body">
              <div v-for="(line, i) in l3CurrentRef" :key="i" class="l3-ref-line">{{ line }}</div>
              <div class="l3-divider"></div>
              <div class="l3-task-text">{{ l3CurrentDesc }}</div>
            </div>
          </div>
          <div class="l3-editor-panel">
            <div class="l3-panel-header">你的SQL</div>
            <textarea class="l3-editor" v-model="l3Answer" placeholder="在此输入SQL语句..." spellcheck="false"></textarea>
          </div>
        </div>

        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l3Task > 3 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l3Task > 3 ? '恭喜通关！所有数据操作完成！' : '回答正确！进入下一题') : l3Feedback || 'SQL语句不正确，请检查语法和逻辑' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 4" class="level-4">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第四关</span>
            <span class="level-label">视图与存储过程</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel4">重置</button>
            <button class="btn btn-primary" @click="checkLevel4">验证顺序</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>将左侧打乱的SQL代码块拖拽到右侧槽位中，按正确顺序排列。
          <span style="margin-left:12px">进度：第{{ l4Task }}题 / 共3题</span>
        </div>
        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l4Task - 1) / 3 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l4Task > 1, current: l4Task === 1 }">1. 客户视图</span>
            <span :class="{ done: l4Task > 2, current: l4Task === 2 }">2. 银行卡视图</span>
            <span :class="{ current: l4Task === 3 }">3. 查余额存储过程</span>
          </div>
        </div>
        <div class="l4-workspace">
          <div class="l4-pieces-panel">
            <div class="l4-panel-header">代码块（拖拽到右侧）</div>
            <div class="l4-pieces-list">
              <div v-for="piece in l4CurrentPieces" :key="piece.id" class="l4-piece"
                :class="{ used: piece.used }"
                :draggable="!piece.used"
                @dragstart="onL4DragStart($event, piece)">
                <code>{{ piece.text }}</code>
              </div>
            </div>
          </div>
          <div class="l4-slots-panel">
            <div class="l4-panel-header">代码槽位（按顺序排列）</div>
            <div class="l4-slots-list">
              <div v-for="slot in l4CurrentSlots" :key="slot.id" class="l4-slot"
                :class="{ filled: slot.filledPieceId, correct: slot.checked && slot.correct, wrong: slot.checked && !slot.correct }"
                @dragover.prevent @drop="onL4Drop($event, slot)">
                <span v-if="slot.filledPieceId" class="l4-slot-text">{{ l4GetPieceText(slot.filledPieceId) }}</span>
                <span v-else class="l4-slot-placeholder">{{ slot.hint }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l4Task > 3 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l4Task > 3 ? '恭喜通关！所有代码块排列正确！' : '排列正确！进入下一题') : '代码块顺序不正确，请重新排列' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 5" class="level-5">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第五关</span>
            <span class="level-label">触发器与事务</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel5">重置</button>
            <button class="btn btn-primary" @click="checkLevel5">验证连线</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>点击源节点，再点击目标节点，画出流程连线。将银行业务流程走通。
          <span style="margin-left:12px">进度：第{{ l5Task }}题 / 共2题</span>
        </div>
        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l5Task - 1) / 2 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l5Task > 1, current: l5Task === 1 }">1. 自动开卡触发器</span>
            <span :class="{ current: l5Task === 2 }">2. 转账事务流程</span>
          </div>
        </div>
        <div class="l5-workspace">
          <svg class="l5-canvas" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6"/></marker></defs>
            <g v-for="node in l5CurrentNodes" :key="node.id" @click="onL5NodeClick(node)">
              <rect :x="node.x - 70" :y="node.y - 22" width="140" height="44" rx="8"
                :fill="l5SelectedNode === node.id ? '#dbeafe' : node.type === 'action' ? '#f0fdf4' : node.type === 'decision' ? '#fef3c7' : '#f8fafc'"
                :stroke="l5SelectedNode === node.id ? '#3b82f6' : '#94a3b8'" stroke-width="2" class="l5-node-rect"/>
              <text :x="node.x" :y="node.y + 5" text-anchor="middle" fill="#1e293b" font-size="12" font-weight="600">{{ node.label }}</text>
            </g>
            <g v-for="(line, idx) in l5CurrentLines" :key="'line'+idx">
              <line :x1="line.x1" :y1="line.y1" :x2="line.x2" :y2="line.y2" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrowhead)"/>
            </g>
          </svg>
          <div class="l5-info-panel">
            <div class="l5-panel-header">流程说明</div>
            <div class="l5-task-desc">{{ l5CurrentDesc }}</div>
            <div class="l5-connections">
              <div class="l5-conn-header">已连线：</div>
              <div v-for="(conn, idx) in l5CurrentConnections" :key="idx" class="l5-conn-item">
                {{ conn.from }} → {{ conn.to }}
                <button class="l5-conn-del" @click="removeL5Connection(idx)">×</button>
              </div>
              <div v-if="l5CurrentConnections.length === 0" class="l5-conn-empty">暂无连线</div>
            </div>
          </div>
        </div>
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l5Task > 2 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l5Task > 2 ? '恭喜通关！所有流程连线正确！' : '连线正确！进入下一题') : '流程连线不正确，请检查' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 6" class="level-6">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第六关</span>
            <span class="level-label">性能调优</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel6">重置</button>
            <button class="btn btn-primary" @click="checkLevel6Task">{{ l6Task < 3 ? '提交本题' : '验证全部' }}</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>阅读慢查询场景和优化提示，手动编写优化后的SQL语句。
          <span style="margin-left:12px">进度：第{{ l6Task }}题 / 共3题</span>
        </div>
        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l6Task - 1) / 3 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l6Task > 1, current: l6Task === 1 }">1. 分区表优化</span>
            <span :class="{ done: l6Task > 2, current: l6Task === 2 }">2. 索引优化</span>
            <span :class="{ current: l6Task === 3 }">3. 子查询改写</span>
          </div>
        </div>
        <div class="l3-workspace">
          <div class="l3-ref-panel">
            <div class="l3-panel-header">慢查询场景</div>
            <div class="l3-ref-body">
              <div class="l6-scenario-block">
                <div class="l6-scenario-label">原始SQL</div>
                <div class="l6-query-display">{{ l6CurrentTask.query }}</div>
              </div>
              <div class="l6-scenario-block">
                <div class="l6-scenario-label">当前耗时</div>
                <div class="l6-time-slow">{{ l6CurrentTask.currentTime }}</div>
              </div>
              <div class="l6-scenario-block">
                <div class="l6-scenario-label">优化提示</div>
                <div class="l6-hint-text">{{ l6CurrentTask.hint }}</div>
              </div>
              <div class="l6-scenario-block">
                <div class="l6-scenario-label">参考示例</div>
                <div v-for="(line, i) in l6CurrentTask.ref" :key="i" class="l3-ref-line">{{ line }}</div>
              </div>
            </div>
          </div>
          <div class="l3-editor-panel">
            <div class="l3-panel-header">你的优化SQL</div>
            <textarea class="l3-editor" v-model="l6Answer" placeholder="在此输入优化后的SQL语句..." spellcheck="false"></textarea>
          </div>
        </div>
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l6Task > 3 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l6Task > 3 ? '恭喜通关！你已成为DBA调优专家！' : '优化正确！进入下一题') : l6Feedback || 'SQL优化不正确，请检查语法和优化策略' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 7" class="level-7">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第七关</span>
            <span class="level-label">数据库安全与权限</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel7">重置</button>
            <button class="btn btn-primary" @click="checkLevel7Part">{{ l7Part < 3 ? '提交本部分' : '验证答案' }}</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>补全数据库安全与权限管理的SQL命令。部分空缺需手动输入，部分可从选项中选择。
          <span style="margin-left:12px">进度：第{{ l7Part }}部分 / 共3部分</span>
        </div>
        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l7Part - 1) / 3 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l7Part > 1, current: l7Part === 1 }">1. 角色与用户</span>
            <span :class="{ done: l7Part > 2, current: l7Part === 2 }">2. 权限授予</span>
            <span :class="{ current: l7Part === 3 }">3. 权限回收与审计</span>
          </div>
        </div>
        <div class="sql-workspace">
          <div class="sql-terminal">
            <div class="terminal-header">
              <span class="terminal-dot red"></span>
              <span class="terminal-dot yellow"></span>
              <span class="terminal-dot green"></span>
              <span class="terminal-title">openGauss Terminal</span>
            </div>
            <div class="terminal-body">
              <div v-for="(line, li) in l7CurrentLines" :key="li" class="sql-line">
                <template v-for="(seg, si) in line" :key="si">
                  <span v-if="seg.type === 'text'" class="sql-text">{{ seg.value }}</span>
                  <template v-else>
                    <span v-if="l7BlankMeta[seg.blankId]?.mode === 'select'" class="sql-blank"
                      :class="{ filled: l7Blanks[seg.blankId]?.filled, correct: l7Blanks[seg.blankId]?.checked && l7Blanks[seg.blankId]?.correct, wrong: l7Blanks[seg.blankId]?.checked && !l7Blanks[seg.blankId]?.correct }"
                      @click="l7ActiveBlank = seg.blankId">
                      {{ l7Blanks[seg.blankId]?.filled ? l7Blanks[seg.blankId]?.value : '____' }}
                    </span>
                    <input v-else class="sql-input"
                      :class="{ correct: l7Blanks[seg.blankId]?.checked && l7Blanks[seg.blankId]?.correct, wrong: l7Blanks[seg.blankId]?.checked && !l7Blanks[seg.blankId]?.correct }"
                      :value="l7Blanks[seg.blankId]?.value || ''"
                      @input="onL7Input(seg.blankId, ($event.target as HTMLInputElement).value)"
                      @focus="l7ActiveBlank = seg.blankId"
                      :placeholder="'输入答案'" />
                  </template>
                </template>
              </div>
            </div>
          </div>
          <div class="sql-options">
            <div class="options-header">答题面板</div>
            <template v-if="l7ActiveBlank !== null && l7BlankMeta[l7ActiveBlank]?.mode === 'select'">
              <div class="options-target">第{{ l7ActiveBlank + 1 }}空 — 选择题</div>
              <div class="options-list">
                <button v-for="opt in l7CurrentOptions" :key="opt" class="option-btn"
                  :class="{ selected: l7Blanks[l7ActiveBlank]?.value === opt }"
                  @click="selectL7Option(opt)">
                  {{ opt }}
                </button>
              </div>
            </template>
            <template v-else-if="l7ActiveBlank !== null && l7BlankMeta[l7ActiveBlank]?.mode === 'input'">
              <div class="options-target">第{{ l7ActiveBlank + 1 }}空 — 填空题</div>
              <div class="options-hint">请在代码中直接输入答案</div>
              <div class="options-hint" style="margin-top:8px;color:#64748b;">提示：{{ l7BlankMeta[l7ActiveBlank]?.hint }}</div>
            </template>
            <div v-else class="options-hint">点击选择题空缺处显示选项</div>
          </div>
        </div>
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l7Part > 3 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l7Part > 3 ? '恭喜通关！你已掌握数据库安全管理！' : '本部分通过！进入下一部分') : '部分空缺填写不正确，请检查红色标记处' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 8" class="level-8">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第八关</span>
            <span class="level-label">备份与恢复</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel8">重置</button>
            <button class="btn btn-primary" @click="checkLevel8">验证顺序</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>将左侧打乱的备份/恢复命令步骤拖拽到右侧槽位中，按正确顺序排列。
          <span style="margin-left:12px">进度：第{{ l8Task }}题 / 共2题</span>
        </div>
        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l8Task - 1) / 2 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l8Task > 1, current: l8Task === 1 }">1. 逻辑备份</span>
            <span :class="{ current: l8Task === 2 }">2. 数据恢复</span>
          </div>
        </div>
        <div class="l4-workspace">
          <div class="l4-pieces-panel">
            <div class="l4-panel-header">命令步骤（拖拽到右侧）</div>
            <div class="l4-pieces-list">
              <div v-for="piece in l8CurrentPieces" :key="piece.id" class="l4-piece"
                :class="{ used: piece.used }"
                :draggable="!piece.used"
                @dragstart="onL8DragStart($event, piece)">
                <code>{{ piece.text }}</code>
              </div>
            </div>
          </div>
          <div class="l4-slots-panel">
            <div class="l4-panel-header">执行顺序（按顺序排列）</div>
            <div class="l4-slots-list">
              <div v-for="slot in l8CurrentSlots" :key="slot.id" class="l4-slot"
                :class="{ filled: slot.filledPieceId, correct: slot.checked && slot.correct, wrong: slot.checked && !slot.correct }"
                @dragover.prevent @drop="onL8Drop($event, slot)">
                <span v-if="slot.filledPieceId" class="l4-slot-text">{{ l8GetPieceText(slot.filledPieceId) }}</span>
                <span v-else class="l4-slot-placeholder">{{ slot.hint }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l8Task > 2 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l8Task > 2 ? '恭喜通关！你已掌握数据库备份与恢复！' : '排列正确！进入下一题') : '步骤顺序不正确，请重新排列' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>

      <div v-else-if="currentLevel === 9" class="level-9">
        <div class="level-header">
          <button class="btn" @click="currentLevel = 0">← 返回</button>
          <div class="level-info">
            <span class="level-badge">第九关</span>
            <span class="level-label">综合实战：Bug猎人</span>
          </div>
          <div class="level-actions">
            <button class="btn" @click="resetLevel9">重置</button>
            <button class="btn btn-primary" @click="checkLevel9Task">{{ l9Task < 3 ? '提交本题' : '验证全部' }}</button>
          </div>
        </div>
        <div class="level-hint">
          <strong>任务说明：</strong>每段SQL代码都有Bug，找出错误并写出修正后的完整SQL。
          <span style="margin-left:12px">进度：第{{ l9Task }}题 / 共3题</span>
        </div>
        <div class="l2-progress">
          <div class="l2-progress-bar">
            <div class="l2-progress-fill" :style="{ width: ((l9Task - 1) / 3 * 100) + '%' }"></div>
          </div>
          <div class="l2-progress-steps">
            <span :class="{ done: l9Task > 1, current: l9Task === 1 }">1. 建表Bug</span>
            <span :class="{ done: l9Task > 2, current: l9Task === 2 }">2. 视图Bug</span>
            <span :class="{ current: l9Task === 3 }">3. 存储过程Bug</span>
          </div>
        </div>
        <div class="l3-workspace">
          <div class="l3-ref-panel">
            <div class="l3-panel-header">有Bug的代码</div>
            <div class="l3-ref-body">
              <div class="l9-bug-hint">Bug提示：{{ l9CurrentTask.bugHint }}</div>
              <div class="l9-divider"></div>
              <div v-for="(line, i) in l9CurrentTask.buggyCode" :key="i" class="l3-ref-line">{{ line }}</div>
            </div>
          </div>
          <div class="l3-editor-panel">
            <div class="l3-panel-header">修正后的SQL</div>
            <textarea class="l3-editor" v-model="l9Answer" placeholder="在此输入修正后的SQL语句..." spellcheck="false"></textarea>
          </div>
        </div>
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box" :class="{ success: modalSuccess, fail: !modalSuccess }">
            <div class="modal-icon">{{ modalSuccess ? (l9Task > 3 ? '🎉' : '✅') : '❌' }}</div>
            <div class="modal-text">{{ modalSuccess ? (l9Task > 3 ? '恭喜通关！你已是SQL Bug猎人大师！' : '修正正确！进入下一题') : l9Feedback || 'SQL修正不正确，请再仔细检查' }}</div>
            <button class="btn" :class="{ 'btn-primary': modalSuccess }" @click="showModal=false">确定</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLearningStore } from '../stores/learning'

const store = useLearningStore()

const currentLevel = ref(0)
const showRef = ref(false)
const showModal = ref(false)
const modalSuccess = ref(false)
const showIntroModal = ref(false)
const introLevel = ref(0)

const levelAttempts = ref<Record<number, number>>({ 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0 })
const levelStartTime = ref<Record<number, number>>({})

const abilityDims = ['基础环境搭建', 'openGauss运维', '数据库迁移与同步', '数据库开发', '数据库设计', '数据库优化与调优', 'SQL编程与优化', '数据库对象管理']
const abilities = ref([10, 10, 10, 10, 10, 10, 10, 10])

const completedLevels = computed(() => store.completedLevels)

const levelIntros: Record<number, { title: string; desc: string; skills: string[]; boost: number[] }> = {
  1: {
    title: '第一关 — ER图复位',
    desc: '根据银行业务系统的ER关系图，将拆散的实体、关系和属性组件拖拽回正确位置。通过本关，你将理解实体-联系模型的基本概念，掌握实体、属性、关系之间的连接方式。',
    skills: ['数据库设计', 'ER模型理解', '实体关系分析'],
    boost: [0, 0, 0, 0, 25, 0, 0, 10],
  },
  2: {
    title: '第二关 — SQL建库建表',
    desc: '在openGauss终端中补全SQL命令，完成数据库创建、用户授权、模式设置、表创建及约束添加。通过本关，你将掌握openGauss数据库的全生命周期建库建表操作。',
    skills: ['基础环境搭建', 'SQL DDL语法', '约束设计', '数据库对象管理'],
    boost: [20, 10, 0, 15, 10, 0, 15, 20],
  },
  3: {
    title: '第三关 — 数据录入与修改',
    desc: '根据银行业务场景，仿写INSERT和UPDATE语句完成数据录入、修改密码和挂失操作。通过本关，你将掌握DML语句的编写，理解数据插入与更新的实际应用。',
    skills: ['SQL DML语法', 'INSERT语句', 'UPDATE语句', '数据维护'],
    boost: [0, 0, 0, 20, 5, 0, 30, 10],
  },
  4: {
    title: '第四关 — 视图与存储过程',
    desc: '将打乱的SQL代码块拖拽到正确位置，拼出完整的视图和存储过程。通过本关，你将掌握CREATE VIEW和CREATE PROCEDURE的语法结构。',
    skills: ['视图创建', '存储过程', 'SQL代码结构', '数据库对象管理'],
    boost: [0, 0, 0, 15, 0, 10, 20, 15],
  },
  5: {
    title: '第五关 — 触发器与事务',
    desc: '在流程图中连线，将银行业务的触发器逻辑和事务流程走通。通过本关，你将理解触发器的执行时机和事务的ACID特性。',
    skills: ['触发器设计', '事务管理', 'ROLLBACK', '业务逻辑分析'],
    boost: [0, 0, 0, 10, 0, 20, 15, 10],
  },
  6: {
    title: '第六关 — 性能调优',
    desc: '面对慢查询场景，阅读优化提示和参考示例，手动编写优化后的SQL语句。通过本关，你将掌握分区表创建、索引优化、子查询改写等核心调优技能。',
    skills: ['分区表', '索引优化', '子查询改写', 'SQL性能分析'],
    boost: [10, 15, 10, 0, 0, 30, 10, 0],
  },
  7: {
    title: '第七关 — 数据库安全与权限',
    desc: '补全数据库安全管理的SQL命令，包括角色创建、用户授权、权限回收和审计策略。通过本关，你将掌握openGauss的三权分立安全模型和GRANT/REVOKE语法。',
    skills: ['角色管理', 'GRANT授权', 'REVOKE回收', '审计策略'],
    boost: [5, 20, 5, 0, 0, 10, 5, 20],
  },
  8: {
    title: '第八关 — 备份与恢复',
    desc: '将打乱的gs_dump和gs_restore命令步骤拖拽到正确顺序。通过本关，你将掌握openGauss逻辑备份与恢复的完整流程和参数配置。',
    skills: ['gs_dump备份', 'gs_restore恢复', '备份策略', '灾难恢复'],
    boost: [10, 25, 10, 0, 0, 10, 0, 5],
  },
  9: {
    title: '第九关 — 综合实战：Bug猎人',
    desc: '每段SQL代码都隐藏着Bug，找出错误并写出修正后的完整SQL。通过本关，你将检验对建表、视图、存储过程等知识的综合掌握程度。',
    skills: ['SQL调试', '语法纠错', '逻辑分析', '综合实战'],
    boost: [5, 10, 5, 15, 10, 10, 20, 10],
  },
}

const abilityScore = computed(() => Math.round(abilities.value.reduce((a, b) => a + b, 0) / abilities.value.length))

function showLevelIntro(level: number) {
  introLevel.value = level
  showIntroModal.value = true
}

function radarPoint(index: number, radius: number) {
  const angle = (Math.PI * 2 * (index - 1)) / 8 - Math.PI / 2
  return { x: 150 + radius * Math.cos(angle), y: 150 + radius * Math.sin(angle) }
}

function radarGrid(radius: number) {
  return Array.from({ length: 8 }, (_, i) => {
    const p = radarPoint(i + 1, radius)
    return `${p.x},${p.y}`
  }).join(' ')
}

function radarArea() {
  return Array.from({ length: 8 }, (_, i) => {
    const p = radarPoint(i + 1, abilities.value[i] * 0.8)
    return `${p.x},${p.y}`
  }).join(' ')
}

interface FixedItem {
  id: string
  shape: 'rect' | 'ellipse' | 'diamond'
  x: number
  y: number
  rx?: number
  label: string
  pk?: boolean
}

interface RemovableSlot {
  id: string
  shape: 'rect' | 'ellipse' | 'diamond'
  x: number
  y: number
  rx?: number
  pk?: boolean
  expectedPieceId: string
  matchLabel: string
  matched: boolean
  wrong: boolean
}

interface Piece {
  id: string
  shape: 'rect' | 'ellipse' | 'diamond'
  label: string
  used: boolean
}

const fixedItems: FixedItem[] = [
  { id: 'f-ent-cust', shape: 'rect', x: 150, y: 350, label: '客户' },
  { id: 'f-ent-card', shape: 'rect', x: 550, y: 350, label: '银行卡' },
  { id: 'f-rel-use', shape: 'diamond', x: 340, y: 350, label: '使用' },
  { id: 'f-rel-rec', shape: 'diamond', x: 550, y: 510, label: '记录' },
  { id: 'fa-cust-1', shape: 'ellipse', x: 50, y: 180, rx: 50, label: '客户编号', pk: true },
  { id: 'fa-cust-2', shape: 'ellipse', x: 170, y: 150, rx: 45, label: '客户姓名' },
  { id: 'fa-cust-3', shape: 'ellipse', x: 290, y: 180, rx: 42, label: '身份证号' },
  { id: 'fa-cust-4', shape: 'ellipse', x: 60, y: 520, rx: 42, label: '联系电话' },
  { id: 'fa-cust-5', shape: 'ellipse', x: 240, y: 520, rx: 42, label: '联系地址' },
  { id: 'fa-card-1', shape: 'ellipse', x: 370, y: 160, rx: 35, label: '卡号', pk: true },
  { id: 'fa-card-2', shape: 'ellipse', x: 490, y: 140, rx: 32, label: '密码' },
  { id: 'fa-card-3', shape: 'ellipse', x: 620, y: 140, rx: 42, label: '是否挂失' },
  { id: 'fa-card-4', shape: 'ellipse', x: 750, y: 160, rx: 32, label: '余额' },
  { id: 'fa-card-5', shape: 'ellipse', x: 440, y: 530, rx: 42, label: '开户日期' },
  { id: 'fa-card-6', shape: 'ellipse', x: 660, y: 530, rx: 42, label: '开户金额' },
  { id: 'fa-card-7', shape: 'ellipse', x: 550, y: 160, rx: 42, label: '顾客编号' },
  { id: 'fa-dep-2', shape: 'ellipse', x: 1020, y: 220, rx: 42, label: '存款名称' },
  { id: 'fa-dep-3', shape: 'ellipse', x: 1140, y: 250, rx: 42, label: '存款描述' },
  { id: 'fa-tran-1', shape: 'ellipse', x: 360, y: 700, rx: 42, label: '交易时间' },
  { id: 'fa-tran-2', shape: 'ellipse', x: 510, y: 720, rx: 42, label: '交易类型' },
  { id: 'fa-tran-4', shape: 'ellipse', x: 680, y: 720, rx: 32, label: '卡号' },
  { id: 'fa-tran-5', shape: 'ellipse', x: 830, y: 700, rx: 32, label: '备注' },
]

const fixedAttrLines = [
  { id: 'al1', x1: 150, y1: 330, x2: 50, y2: 197 },
  { id: 'al2', x1: 150, y1: 330, x2: 170, y2: 167 },
  { id: 'al3', x1: 150, y1: 330, x2: 290, y2: 197 },
  { id: 'al4', x1: 150, y1: 370, x2: 60, y2: 503 },
  { id: 'al5', x1: 150, y1: 370, x2: 240, y2: 503 },
  { id: 'al6', x1: 550, y1: 330, x2: 370, y2: 177 },
  { id: 'al7', x1: 550, y1: 330, x2: 490, y2: 157 },
  { id: 'al8', x1: 550, y1: 330, x2: 620, y2: 157 },
  { id: 'al9', x1: 550, y1: 330, x2: 750, y2: 177 },
  { id: 'al10', x1: 550, y1: 330, x2: 550, y2: 177 },
  { id: 'al11', x1: 550, y1: 370, x2: 440, y2: 513 },
  { id: 'al12', x1: 550, y1: 370, x2: 660, y2: 513 },
  { id: 'al13', x1: 870, y1: 330, x2: 1020, y2: 237 },
  { id: 'al14', x1: 920, y1: 330, x2: 1140, y2: 267 },
  { id: 'al15', x1: 820, y1: 330, x2: 850, y2: 223 },
  { id: 'al16', x1: 550, y1: 620, x2: 360, y2: 683 },
  { id: 'al17', x1: 550, y1: 620, x2: 510, y2: 703 },
  { id: 'al18', x1: 550, y1: 620, x2: 680, y2: 703 },
  { id: 'al19', x1: 550, y1: 620, x2: 830, y2: 683 },
  { id: 'al20', x1: 550, y1: 620, x2: 600, y2: 693 },
]

const removableSlots = ref<RemovableSlot[]>([
  { id: 's-deposit', shape: 'rect', x: 870, y: 350, expectedPieceId: 'p-deposit', matchLabel: '存款类型', matched: false, wrong: false },
  { id: 's-transaction', shape: 'rect', x: 550, y: 600, expectedPieceId: 'p-transaction', matchLabel: '交易信息', matched: false, wrong: false },
  { id: 's-belong', shape: 'diamond', x: 685, y: 350, expectedPieceId: 'p-belong', matchLabel: '属于', matched: false, wrong: false },
  { id: 's-dep-id', shape: 'ellipse', x: 850, y: 200, rx: 42, pk: true, expectedPieceId: 'p-dep-id', matchLabel: '存款编号', matched: false, wrong: false },
  { id: 's-tran-amt', shape: 'ellipse', x: 600, y: 710, rx: 42, expectedPieceId: 'p-tran-amt', matchLabel: '交易金额', matched: false, wrong: false },
])

const pieces = ref<Piece[]>([
  { id: 'p-deposit', shape: 'rect', label: '存款类型', used: false },
  { id: 'p-transaction', shape: 'rect', label: '交易信息', used: false },
  { id: 'p-belong', shape: 'diamond', label: '属于', used: false },
  { id: 'p-dep-id', shape: 'ellipse', label: '存款编号', used: false },
  { id: 'p-tran-amt', shape: 'ellipse', label: '交易金额', used: false },
])

let draggedPieceId: string | null = null

function startLevel(level: number) {
  showIntroModal.value = false
  currentLevel.value = level
  levelStartTime.value[level] = Date.now()
  store.recordEvent('challenge_start', level)
  if (level === 1) resetLevel1()
  if (level === 2) {
    if (l2PartSaved.value > 1) {
      l2Part.value = l2PartSaved.value
      l2ActiveBlank.value = null
    } else {
      resetLevel2()
    }
  }
  if (level === 3) {
    if (l3TaskSaved.value > 1) {
      l3Task.value = l3TaskSaved.value
      l3Answer.value = ''
      l3Feedback.value = ''
    } else {
      resetLevel3()
    }
  }
  if (level === 4) {
    if (l4TaskSaved.value > 1) {
      l4Task.value = l4TaskSaved.value
    } else {
      resetLevel4()
    }
  }
  if (level === 5) {
    if (l5TaskSaved.value > 1) {
      l5Task.value = l5TaskSaved.value
    } else {
      resetLevel5()
    }
  }
  if (level === 6) {
    if (l6TaskSaved.value > 1) {
      l6Task.value = l6TaskSaved.value
      l6Answer.value = ''
      l6Feedback.value = ''
    } else {
      resetLevel6()
    }
  }
  if (level === 7) {
    if (l7PartSaved.value > 1) {
      l7Part.value = l7PartSaved.value
      l7ActiveBlank.value = null
    } else {
      resetLevel7()
    }
  }
  if (level === 8) {
    if (l8TaskSaved.value > 1) {
      l8Task.value = l8TaskSaved.value
    } else {
      resetLevel8()
    }
  }
  if (level === 9) {
    if (l9TaskSaved.value > 1) {
      l9Task.value = l9TaskSaved.value
      l9Answer.value = ''
      l9Feedback.value = ''
    } else {
      resetLevel9()
    }
  }
}

function resetLevel1() {
  showModal.value = false
  removableSlots.value.forEach(s => { s.matched = false; s.wrong = false })
  pieces.value.forEach(p => { p.used = false })
}

function onDragStart(_e: DragEvent, piece: Piece) {
  draggedPieceId = piece.id
}

function onDropSlot(_e: DragEvent, slot: RemovableSlot) {
  if (!draggedPieceId || slot.matched) return
  const piece = pieces.value.find(p => p.id === draggedPieceId)
  if (!piece || piece.used) return
  const prevSlot = removableSlots.value.find(s => s.matched && s.expectedPieceId === draggedPieceId)
  if (prevSlot) { prevSlot.matched = false; prevSlot.wrong = false }
  piece.used = true
  slot.matched = true
  slot.matchLabel = piece.label
  slot.wrong = false
  draggedPieceId = null
}

function checkLevel1() {
  const allPlaced = removableSlots.value.every(s => s.matched)
  if (!allPlaced) {
    modalSuccess.value = false
    showModal.value = true
    return
  }
  const wrongSlots = removableSlots.value.filter(s => s.expectedPieceId !== pieces.value.find(p => p.label === s.matchLabel)?.id)
  if (wrongSlots.length > 0) {
    modalSuccess.value = false
    showModal.value = true
    levelAttempts.value[1] = (levelAttempts.value[1] || 0) + 1
    store.recordEvent('challenge_error', 1, undefined, {
      category: 'ER图组件放置错误',
      description: `错误放置了: ${wrongSlots.map(s => s.matchLabel).join(', ')}`,
      ability_dim: '数据库设计',
      user_answer: wrongSlots.map(s => s.matchLabel).join(', '),
    })
    return
  }
  modalSuccess.value = true
  showModal.value = true
  levelAttempts.value[1] = (levelAttempts.value[1] || 0) + 1
  if (!completedLevels.value.has(1)) {
    const duration = levelStartTime.value[1] ? Math.floor((Date.now() - levelStartTime.value[1]) / 1000) : 0
    store.recordEvent('challenge_pass', 1, undefined, {
      attempts: levelAttempts.value[1],
      duration_seconds: duration,
    })
    applyBoost(1)
  }
}

// ===== Level 2 =====
type Seg = { type: 'text'; value: string } | { type: 'blank'; blankId: number }

interface L2BlankMeta {
  mode: 'select' | 'input'
  answer: string
  options?: string[]
  hint?: string
}

const l2Part = ref(1)
const l2ActiveBlank = ref<number | null>(null)
const l2PartSaved = ref(1)

interface L2BlankState {
  filled: boolean
  value: string
  checked: boolean
  correct: boolean
}

const l2Blanks = ref<Record<number, L2BlankState>>({})

const l2BlankMeta: Record<number, L2BlankMeta> = {
  0: { mode: 'input', answer: 'su', hint: 'Linux切换用户命令' },
  1: { mode: 'select', answer: 'postgres', options: ['bankdb', 'postgres', 'openGauss', 'mysql'] },
  2: { mode: 'select', answer: 'CREATE', options: ['MAKE', 'ADD', 'CREATE', 'NEW'] },
  3: { mode: 'input', answer: 'CREATE', hint: 'SQL创建用户的关键字' },
  4: { mode: 'select', answer: 'WITH', options: ['USING', 'BY', 'WITH', 'SET'] },
  5: { mode: 'select', answer: 'GRANT', options: ['GIVE', 'GRANT', 'ALLOW', 'SET'] },
  6: { mode: 'input', answer: 'TO', hint: '授权给某人用什么介词' },
  7: { mode: 'select', answer: 'CREATE', options: ['BUILD', 'ADD', 'NEW', 'CREATE'] },
  8: { mode: 'input', answer: 'SET', hint: '设置搜索路径的SQL命令' },
  9: { mode: 'select', answer: 'TO', options: ['AS', 'FOR', 'TO', 'INTO'] },
  10: { mode: 'input', answer: 'SERIAL', hint: 'openGauss自增列类型' },
  11: { mode: 'select', answer: 'NOT', options: ['IS', 'NO', 'NOT', 'MUST'] },
  12: { mode: 'input', answer: 'DEFAULT', hint: '设置列的默认值关键字' },
  13: { mode: 'select', answer: 'DEFAULT', options: ['AUTO', 'DEFAULT', 'SET', 'USE'] },
  14: { mode: 'input', answer: 'DEFAULT', hint: '设置列的默认值关键字' },
  15: { mode: 'select', answer: 'NULL', options: ['BLANK', 'NONE', 'NULL', 'EMPTY'] },
  16: { mode: 'input', answer: 'SERIAL', hint: 'openGauss自增列类型' },
  17: { mode: 'input', answer: 'ALTER', hint: '修改表结构用什么SQL命令' },
  18: { mode: 'select', answer: 'ADD', options: ['SET', 'CREATE', 'ADD', 'INSERT'] },
  19: { mode: 'input', answer: 'CHECK', hint: '检查约束的关键字' },
  20: { mode: 'select', answer: 'FOREIGN', options: ['OUTER', 'FOREIGN', 'PRIMARY', 'REMOTE'] },
  21: { mode: 'input', answer: 'REFERENCES', hint: '外键引用另一张表的关键字' },
  22: { mode: 'select', answer: 'CHECK', options: ['VALID', 'CHECK', 'VERIFY', 'TEST'] },
  23: { mode: 'input', answer: 'IN', hint: '限定取值范围用什么关键字' },
}

const l2PartLines: Record<number, Seg[][]> = {
  1: [
    [{ type: 'text', value: '-- 步骤1: 切换到openGauss用户' }],
    [{ type: 'blank', blankId: 0 }, { type: 'text', value: ' openGauss' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤2: 进入openGauss命令行' }],
    [{ type: 'text', value: 'gsql -d ' }, { type: 'blank', blankId: 1 }, { type: 'text', value: ' -p 5432' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤3: 创建银行业务系统数据库' }],
    [{ type: 'blank', blankId: 2 }, { type: 'text', value: ' DATABASE bankdb;' }],
  ],
  2: [
    [{ type: 'text', value: '-- 步骤4: 创建数据库用户' }],
    [{ type: 'blank', blankId: 3 }, { type: 'text', value: ' USER bank_admin ' }, { type: 'blank', blankId: 4 }, { type: 'text', value: ' PASSWORD "Bank@1234";' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤5: 授予用户权限' }],
    [{ type: 'blank', blankId: 5 }, { type: 'text', value: ' ALL PRIVILEGES ON DATABASE bankdb ' }, { type: 'blank', blankId: 6 }, { type: 'text', value: ' bank_admin;' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤6: 创建模式并设置搜索路径' }],
    [{ type: 'blank', blankId: 7 }, { type: 'text', value: ' SCHEMA bank_schema;' }],
    [{ type: 'blank', blankId: 8 }, { type: 'text', value: ' SEARCH_PATH ' }, { type: 'blank', blankId: 9 }, { type: 'text', value: ' bank_schema;' }],
  ],
  3: [
    [{ type: 'text', value: '-- 步骤7: 创建用户信息表' }],
    [{ type: 'text', value: 'CREATE TABLE userInfo' }],
    [{ type: 'text', value: '(' }],
    [{ type: 'text', value: '  customerID  ' }, { type: 'blank', blankId: 10 }, { type: 'text', value: ' PRIMARY KEY,' }],
    [{ type: 'text', value: '  customerName CHAR(8) ' }, { type: 'blank', blankId: 11 }, { type: 'text', value: ' NULL,' }],
    [{ type: 'text', value: '  PID CHAR(18) NOT NULL,' }],
    [{ type: 'text', value: '  telephone CHAR(20) NOT NULL,' }],
    [{ type: 'text', value: '  address VARCHAR(50)' }],
    [{ type: 'text', value: ');' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤8: 创建银行卡信息表' }],
    [{ type: 'text', value: 'CREATE TABLE cardInfo' }],
    [{ type: 'text', value: '(' }],
    [{ type: 'text', value: '  cardID  CHAR(17) PRIMARY KEY,' }],
    [{ type: 'text', value: '  curID  VARCHAR(10) ' }, { type: 'blank', blankId: 12 }, { type: 'text', value: " 'RMB' NOT NULL," }],
    [{ type: 'text', value: '  openDate  TIMESTAMP NOT NULL ' }, { type: 'blank', blankId: 13 }, { type: 'text', value: ' CURRENT_TIMESTAMP,' }],
    [{ type: 'text', value: '  IsReportLoss VARCHAR(3) NOT NULL ' }, { type: 'blank', blankId: 14 }, { type: 'text', value: " '否'" }],
    [{ type: 'text', value: ');' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤9: 创建交易信息表' }],
    [{ type: 'text', value: 'CREATE TABLE tradeInfo' }],
    [{ type: 'text', value: '(' }],
    [{ type: 'text', value: '  tradeType  CHAR(6) NOT ' }, { type: 'blank', blankId: 15 }, { type: 'text', value: ',' }],
    [{ type: 'text', value: '  tradeMoney  NUMERIC(18,2) NOT NULL,' }],
    [{ type: 'text', value: '  remark  TEXT' }],
    [{ type: 'text', value: ');' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤10: 创建存款类型表' }],
    [{ type: 'text', value: 'CREATE TABLE deposit' }],
    [{ type: 'text', value: '(' }],
    [{ type: 'text', value: '  savingID  ' }, { type: 'blank', blankId: 16 }, { type: 'text', value: ' PRIMARY KEY,' }],
    [{ type: 'text', value: '  savingName  VARCHAR(20) NOT NULL,' }],
    [{ type: 'text', value: '  descrip VARCHAR(50)' }],
    [{ type: 'text', value: ');' }],
  ],
  4: [
    [{ type: 'text', value: '-- 步骤11: 为用户信息表添加约束' }],
    [{ type: 'blank', blankId: 17 }, { type: 'text', value: ' TABLE userInfo' }],
    [{ type: 'text', value: '  ' }, { type: 'blank', blankId: 18 }, { type: 'text', value: ' CONSTRAINT chk_PID ' }, { type: 'blank', blankId: 19 }, { type: 'text', value: ' (CHAR_LENGTH(CAST(PID AS TEXT)) = 18),' }],
    [{ type: 'text', value: "  ADD CONSTRAINT chk_telephone CHECK (CHAR_LENGTH(REGEXP_REPLACE(CAST(telephone AS TEXT), '[^0-9]', '', 'g')) = 11);" }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤12: 为银行卡信息表添加约束' }],
    [{ type: 'text', value: 'ALTER TABLE cardInfo' }],
    [{ type: 'text', value: '  ADD CONSTRAINT ck_cardid CHECK (' }],
    [{ type: 'text', value: "    SUBSTRING(cardID, 1, 8) = '10103576'" }],
    [{ type: 'text', value: "    AND SUBSTRING(cardID, 9) ~ '^[0-9]{8}$'" }],
    [{ type: 'text', value: '  ),' }],
    [{ type: 'text', value: '  ADD CONSTRAINT CK_openMoney CHECK (openMoney >= 1),' }],
    [{ type: 'text', value: '  ADD CONSTRAINT CK_balance CHECK (balance >= 1),' }],
    [{ type: 'text', value: "  ADD CONSTRAINT CK_pass CHECK (LENGTH(pass) = 6 AND pass ~ '^[0-9]+$')," }],
    [{ type: 'text', value: '  ADD CONSTRAINT FK_customerID ' }, { type: 'blank', blankId: 20 }, { type: 'text', value: ' KEY(customerID) ' }, { type: 'blank', blankId: 21 }, { type: 'text', value: ' userInfo(customerID),' }],
    [{ type: 'text', value: '  ADD CONSTRAINT FK_savingID FOREIGN KEY(savingID) REFERENCES deposit(savingID);' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤13: 为交易信息表添加约束' }],
    [{ type: 'text', value: 'ALTER TABLE tradeInfo' }],
    [{ type: 'text', value: '  ADD CONSTRAINT CK_tradeType ' }, { type: 'blank', blankId: 22 }, { type: 'text', value: ' (tradeType ' }, { type: 'blank', blankId: 23 }, { type: 'text', value: " ('存入', '支取'))," }],
    [{ type: 'text', value: '  ADD CONSTRAINT CK_tradeMoney CHECK (tradeMoney > 0);' }],
  ],
}

function getL2PartBlankIds(part: number): number[] {
  const ids: number[] = []
  const lines = l2PartLines[part]
  if (!lines) return ids
  for (const line of lines) {
    for (const seg of line) {
      if (seg.type === 'blank') ids.push(seg.blankId)
    }
  }
  return ids
}

const l2CurrentLines = computed(() => l2PartLines[l2Part.value] || [])

const l2CurrentOptions = computed(() => {
  if (l2ActiveBlank.value === null) return []
  const meta = l2BlankMeta[l2ActiveBlank.value]
  if (!meta || meta.mode !== 'select') return []
  return meta.options || []
})

function initL2Blanks() {
  const b: Record<number, L2BlankState> = {}
  for (const id of Object.keys(l2BlankMeta)) {
    b[Number(id)] = { filled: false, value: '', checked: false, correct: false }
  }
  l2Blanks.value = b
  l2ActiveBlank.value = null
  l2Part.value = 1
}

function onL2Input(blankId: number, val: string) {
  l2Blanks.value[blankId] = { filled: val.trim().length > 0, value: val.trim(), checked: false, correct: false }
}

function selectL2Option(opt: string) {
  if (l2ActiveBlank.value === null) return
  l2Blanks.value[l2ActiveBlank.value] = { filled: true, value: opt, checked: false, correct: false }
}

function checkLevel2Part() {
  const ids = getL2PartBlankIds(l2Part.value)
  let allCorrect = true
  const wrongBlanks: number[] = []
  for (const id of ids) {
    const b = l2Blanks.value[id]
    const answer = l2BlankMeta[id].answer
    if (!b || !b.filled || b.value.toUpperCase() !== answer.toUpperCase()) {
      allCorrect = false
      wrongBlanks.push(id)
      l2Blanks.value[id] = { filled: b?.filled || false, value: b?.value || '', checked: true, correct: false }
    } else {
      l2Blanks.value[id] = { ...b, checked: true, correct: true }
    }
  }
  if (allCorrect) {
    if (l2Part.value < 4) {
      modalSuccess.value = true
      showModal.value = true
      l2Part.value++
      l2PartSaved.value = l2Part.value
      applyPartialBoost(2, l2Part.value - 1, 4)
    } else {
      modalSuccess.value = true
      showModal.value = true
      levelAttempts.value[2] = (levelAttempts.value[2] || 0) + 1
      if (!completedLevels.value.has(2)) {
        const duration = levelStartTime.value[2] ? Math.floor((Date.now() - levelStartTime.value[2]) / 1000) : 0
        store.recordEvent('challenge_pass', 2, undefined, {
          attempts: levelAttempts.value[2],
          duration_seconds: duration,
        })
        applyBoost(2)
      }
    }
  } else {
    modalSuccess.value = false
    showModal.value = true
    levelAttempts.value[2] = (levelAttempts.value[2] || 0) + 1
    store.recordEvent('challenge_error', 2, l2Part.value, {
      category: 'SQL填空错误',
      description: `第${l2Part.value}部分空缺${wrongBlanks.join(',')}填写错误`,
      ability_dim: 'SQL编程与优化',
      wrong_blank_ids: wrongBlanks,
    })
  }
}

function resetLevel2() {
  showModal.value = false
  initL2Blanks()
  l2PartSaved.value = 1
}

// ===== Level 3 =====
const l3Task = ref(1)
const l3Answer = ref('')
const l3Feedback = ref('')
const l3TaskSaved = ref(1)

interface L3TaskDef {
  ref: string[]
  desc: string
  validate: (sql: string) => { correct: boolean; feedback?: string }
}

const l3Tasks: Record<number, L3TaskDef> = {
  1: {
    ref: [
      '-- 示例：向存款类型表插入数据',
      "INSERT INTO deposit (savingName, descrip)",
      "VALUES ('活期', '按存款日结算利息');",
      '',
      '-- 示例：向用户信息表插入数据',
      "INSERT INTO userInfo (customerid, customerName, PID, telephone)",
      "VALUES (2, 'Jane', '110000000000000002', '13900000002');",
      '',
      '-- 示例：向银行卡信息表插入数据',
      "INSERT INTO cardInfo (cardid, curid, savingid, openmoney, balance, pass, isreportloss, customerid)",
      "VALUES ('1010357600000002', 'RMB', 2, 1.00, 1.00, '888888', '否', 2);",
    ],
    desc: `请仿照示例，写出以下3条INSERT语句：
① 向deposit表插入"定期一年"，描述为"存款期是1年"
② 向userInfo表插入客户编号3，姓名Michael，身份证110000000000000003，电话13900000003
③ 向cardInfo表插入卡号1010357600000003，币种RMB，存款类型2，开户金额1.00，余额1.00，密码888888，未挂失，客户编号3`,
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').replace(/;\s*/g, ';\n').trim().toUpperCase()
      const hasDeposit = s.includes('INSERT INTO DEPOSIT') && s.includes('SAVINGNAME') && s.includes('定期一年')
      const hasUser = s.includes('INSERT INTO USERINFO') && s.includes('MICHAEL') && s.includes('110000000000000003')
      const hasCard = s.includes('INSERT INTO CARDINFO') && s.includes('1010357600000003')
      const countInsert = (s.match(/INSERT INTO/g) || []).length
      if (countInsert < 3) return { correct: false, feedback: `需要3条INSERT语句，当前只检测到${countInsert}条` }
      if (!hasDeposit) return { correct: false, feedback: 'deposit表的INSERT语句不正确，请检查表名和值' }
      if (!hasUser) return { correct: false, feedback: 'userInfo表的INSERT语句不正确，请检查姓名和身份证号' }
      if (!hasCard) return { correct: false, feedback: 'cardInfo表的INSERT语句不正确，请检查卡号和列名' }
      return { correct: true }
    },
  },
  2: {
    ref: [
      '-- 示例：修改银行卡密码',
      "UPDATE cardinfo",
      "SET pass = '123456'",
      "WHERE cardid = '1010357600000010';",
      '',
      '-- 含义：将卡号1010357600000010的密码改为123456',
    ],
    desc: '请仿照示例，写出UPDATE语句：将Emily（卡号1010357600000004）的银行卡密码修改为123123',
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasUpdate = s.includes('UPDATE CARDINFO') || s.includes('UPDATE CARDINFO')
      const hasSet = s.includes('SET') && s.includes('PASS') && s.includes('123123')
      const hasWhere = s.includes('WHERE') && s.includes('CARDID') && s.includes('1010357600000004')
      if (!hasUpdate) return { correct: false, feedback: '请使用UPDATE cardInfo语句' }
      if (!hasSet) return { correct: false, feedback: 'SET子句应设置pass = 123123' }
      if (!hasWhere) return { correct: false, feedback: 'WHERE子句应指定cardid = 1010357600000004' }
      return { correct: true }
    },
  },
  3: {
    ref: [
      '-- 示例：挂失银行卡',
      "UPDATE cardinfo",
      "SET isreportloss = '是'",
      "WHERE cardid = '1010357600000007';",
      '',
      '-- 含义：将卡号1010357600000007标记为挂失',
    ],
    desc: '请仿照示例，写出UPDATE语句：将David（卡号1010357600000005）的银行卡设置为挂失状态',
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasUpdate = s.includes('UPDATE CARDINFO')
      const hasSet = s.includes('SET') && s.includes('ISREPORTLOSS') && (s.includes('是') || s.includes("'是'"))
      const hasWhere = s.includes('WHERE') && s.includes('CARDID') && s.includes('1010357600000005')
      if (!hasUpdate) return { correct: false, feedback: '请使用UPDATE cardInfo语句' }
      if (!hasSet) return { correct: false, feedback: 'SET子句应设置isreportloss = 是' }
      if (!hasWhere) return { correct: false, feedback: 'WHERE子句应指定cardid = 1010357600000005' }
      return { correct: true }
    },
  },
}

const l3CurrentRef = computed(() => l3Tasks[l3Task.value]?.ref || [])
const l3CurrentDesc = computed(() => l3Tasks[l3Task.value]?.desc || '')

function resetLevel3() {
  showModal.value = false
  l3Task.value = 1
  l3Answer.value = ''
  l3Feedback.value = ''
  l3TaskSaved.value = 1
}

function checkLevel3Task() {
  const task = l3Tasks[l3Task.value]
  if (!task) return
  const result = task.validate(l3Answer.value)
  if (result.correct) {
    if (l3Task.value < 3) {
      modalSuccess.value = true
      showModal.value = true
      l3Task.value++
      l3TaskSaved.value = l3Task.value
      applyPartialBoost(3, l3Task.value - 1, 3)
      l3Answer.value = ''
      l3Feedback.value = ''
    } else {
      modalSuccess.value = true
      showModal.value = true
      levelAttempts.value[3] = (levelAttempts.value[3] || 0) + 1
      if (!completedLevels.value.has(3)) {
        const duration = levelStartTime.value[3] ? Math.floor((Date.now() - levelStartTime.value[3]) / 1000) : 0
        store.recordEvent('challenge_pass', 3, undefined, {
          attempts: levelAttempts.value[3],
          duration_seconds: duration,
        })
        applyBoost(3)
      }
    }
  } else {
    modalSuccess.value = false
    l3Feedback.value = result.feedback || ''
    showModal.value = true
    levelAttempts.value[3] = (levelAttempts.value[3] || 0) + 1
    store.recordEvent('challenge_error', 3, l3Task.value, {
      category: 'SQL仿写错误',
      description: `第${l3Task.value}题SQL语句不正确`,
      ability_dim: 'SQL编程与优化',
      task_index: l3Task.value,
    })
  }
}

function applyBoost(level: number) {
  const intro = levelIntros[level]
  if (!intro) return
  abilities.value = abilities.value.map((v, i) => Math.min(100, v + (intro.boost[i] || 0)))
}

function applyPartialBoost(level: number, partIndex: number, totalParts: number) {
  const intro = levelIntros[level]
  if (!intro) return
  abilities.value = abilities.value.map((v, i) => {
    const full = intro.boost[i] || 0
    const part = Math.max(1, Math.round(full / totalParts))
    return Math.min(100, v + part)
  })
  store.recordEvent('challenge_part_pass', level, partIndex, { total_parts: totalParts })
}

// ===== Level 4: Code Puzzle =====
interface L4Piece { id: string; text: string; used: boolean }
interface L4Slot { id: string; hint: string; expectedPieceId: string; filledPieceId: string | null; checked: boolean; correct: boolean }

const l4Task = ref(1)
const l4TaskSaved = ref(1)
const l4Version = ref(0)
let l4DraggedPieceId: string | null = null

const l4Tasks: Record<number, { pieces: L4Piece[]; slots: L4Slot[] }> = {
  1: {
    pieces: [
      { id: 'p4-1-3', text: 'AS', used: false },
      { id: 'p4-1-5', text: 'customerID AS "客户编号",', used: false },
      { id: 'p4-1-1', text: 'CREATE VIEW vw_userInfo', used: false },
      { id: 'p4-1-6', text: 'customerName AS "开户名",', used: false },
      { id: 'p4-1-4', text: 'SELECT', used: false },
      { id: 'p4-1-7', text: 'PID AS "身份证号"', used: false },
      { id: 'p4-1-2', text: 'DROP VIEW IF EXISTS vw_userInfo;', used: false },
      { id: 'p4-1-8', text: 'FROM userInfo;', used: false },
    ],
    slots: [
      { id: 's4-1-1', hint: '1. 删除旧视图', expectedPieceId: 'p4-1-2', filledPieceId: null, checked: false, correct: false },
      { id: 's4-1-2', hint: '2. 创建视图', expectedPieceId: 'p4-1-1', filledPieceId: null, checked: false, correct: false },
      { id: 's4-1-3', hint: '3. AS关键字', expectedPieceId: 'p4-1-3', filledPieceId: null, checked: false, correct: false },
      { id: 's4-1-4', hint: '4. SELECT', expectedPieceId: 'p4-1-4', filledPieceId: null, checked: false, correct: false },
      { id: 's4-1-5', hint: '5. 客户编号列', expectedPieceId: 'p4-1-5', filledPieceId: null, checked: false, correct: false },
      { id: 's4-1-6', hint: '6. 开户名列', expectedPieceId: 'p4-1-6', filledPieceId: null, checked: false, correct: false },
      { id: 's4-1-7', hint: '7. 身份证列', expectedPieceId: 'p4-1-7', filledPieceId: null, checked: false, correct: false },
      { id: 's4-1-8', hint: '8. FROM表', expectedPieceId: 'p4-1-8', filledPieceId: null, checked: false, correct: false },
    ],
  },
  2: {
    pieces: [
      { id: 'p4-2-1', text: 'CREATE VIEW vw_cardInfo', used: false },
      { id: 'p4-2-4', text: 'c.cardID AS "卡号",', used: false },
      { id: 'p4-2-2', text: 'AS', used: false },
      { id: 'p4-2-5', text: 'u.customerName AS "客户姓名",', used: false },
      { id: 'p4-2-3', text: 'SELECT', used: false },
      { id: 'p4-2-6', text: 'd.savingName AS "存款类型",', used: false },
      { id: 'p4-2-7', text: 'c.balance AS "余额"', used: false },
      { id: 'p4-2-8', text: 'FROM cardInfo c JOIN deposit d ON c.savingID = d.savingID JOIN userInfo u ON c.customerID = u.customerID;', used: false },
    ],
    slots: [
      { id: 's4-2-1', hint: '1. 创建视图', expectedPieceId: 'p4-2-1', filledPieceId: null, checked: false, correct: false },
      { id: 's4-2-2', hint: '2. AS', expectedPieceId: 'p4-2-2', filledPieceId: null, checked: false, correct: false },
      { id: 's4-2-3', hint: '3. SELECT', expectedPieceId: 'p4-2-3', filledPieceId: null, checked: false, correct: false },
      { id: 's4-2-4', hint: '4. 卡号列', expectedPieceId: 'p4-2-4', filledPieceId: null, checked: false, correct: false },
      { id: 's4-2-5', hint: '5. 客户姓名列', expectedPieceId: 'p4-2-5', filledPieceId: null, checked: false, correct: false },
      { id: 's4-2-6', hint: '6. 存款类型列', expectedPieceId: 'p4-2-6', filledPieceId: null, checked: false, correct: false },
      { id: 's4-2-7', hint: '7. 余额列', expectedPieceId: 'p4-2-7', filledPieceId: null, checked: false, correct: false },
      { id: 's4-2-8', hint: '8. FROM JOIN', expectedPieceId: 'p4-2-8', filledPieceId: null, checked: false, correct: false },
    ],
  },
  3: {
    pieces: [
      { id: 'p4-3-1', text: 'CREATE OR REPLACE PROCEDURE search_balance', used: false },
      { id: 'p4-3-3', text: 'AS', used: false },
      { id: 'p4-3-2', text: '(p_cardid CHAR(19))', used: false },
      { id: 'p4-3-4', text: 'v_balance NUMERIC(18,2);', used: false },
      { id: 'p4-3-7', text: 'SELECT balance INTO v_balance FROM cardInfo WHERE cardID = p_cardid;', used: false },
      { id: 'p4-3-5', text: 'BEGIN', used: false },
      { id: 'p4-3-8', text: 'RAISE NOTICE \'余额为：%元\', v_balance;', used: false },
      { id: 'p4-3-6', text: 'END;', used: false },
    ],
    slots: [
      { id: 's4-3-1', hint: '1. 创建存储过程', expectedPieceId: 'p4-3-1', filledPieceId: null, checked: false, correct: false },
      { id: 's4-3-2', hint: '2. 参数', expectedPieceId: 'p4-3-2', filledPieceId: null, checked: false, correct: false },
      { id: 's4-3-3', hint: '3. AS', expectedPieceId: 'p4-3-3', filledPieceId: null, checked: false, correct: false },
      { id: 's4-3-4', hint: '4. 声明变量', expectedPieceId: 'p4-3-4', filledPieceId: null, checked: false, correct: false },
      { id: 's4-3-5', hint: '5. BEGIN', expectedPieceId: 'p4-3-5', filledPieceId: null, checked: false, correct: false },
      { id: 's4-3-6', hint: '6. END', expectedPieceId: 'p4-3-6', filledPieceId: null, checked: false, correct: false },
      { id: 's4-3-7', hint: '7. 查询赋值', expectedPieceId: 'p4-3-7', filledPieceId: null, checked: false, correct: false },
      { id: 's4-3-8', hint: '8. 输出结果', expectedPieceId: 'p4-3-8', filledPieceId: null, checked: false, correct: false },
    ],
  },
}


const l4CurrentPieces = computed(() => {
  void l4Version.value
  const task = l4Tasks[l4Task.value]
  return task ? [...task.pieces] : []
})
const l4CurrentSlots = computed(() => {
  void l4Version.value
  const task = l4Tasks[l4Task.value]
  return task ? [...task.slots] : []
})

function l4GetPieceText(pieceId: string): string {
  for (const task of Object.values(l4Tasks)) {
    const p = task.pieces.find(pp => pp.id === pieceId)
    if (p) return p.text
  }
  return ''
}

function onL4DragStart(_e: DragEvent, piece: L4Piece) { l4DraggedPieceId = piece.id }
function onL4Drop(_e: DragEvent, slot: L4Slot) {
  if (!l4DraggedPieceId) return
  const task = l4Tasks[l4Task.value]
  if (!task) return
  const piece = task.pieces.find(p => p.id === l4DraggedPieceId)
  if (!piece || piece.used) return
  if (slot.filledPieceId) {
    const prevPiece = task.pieces.find(p => p.id === slot.filledPieceId)
    if (prevPiece) prevPiece.used = false
  }
  piece.used = true
  slot.filledPieceId = piece.id
  slot.checked = false
  l4DraggedPieceId = null
  l4Version.value++
}

function checkLevel4() {
  const task = l4Tasks[l4Task.value]
  if (!task) return
  const allFilled = task.slots.every(s => s.filledPieceId)
  if (!allFilled) { modalSuccess.value = false; showModal.value = true; return }
  const allCorrect = task.slots.every(s => {
    const ok = s.filledPieceId === s.expectedPieceId
    s.checked = true; s.correct = ok
    return ok
  })
  l4Version.value++
  if (allCorrect) {
    if (l4Task.value < 3) {
      modalSuccess.value = true; showModal.value = true
      l4Task.value++; l4TaskSaved.value = l4Task.value
      applyPartialBoost(4, l4Task.value - 1, 3)
    } else {
      modalSuccess.value = true; showModal.value = true
      levelAttempts.value[4] = (levelAttempts.value[4] || 0) + 1
      if (!completedLevels.value.has(4)) {
        store.recordEvent('challenge_pass', 4, undefined, { attempts: levelAttempts.value[4] })
        applyBoost(4)
      }
    }
  } else {
    modalSuccess.value = false; showModal.value = true
    levelAttempts.value[4] = (levelAttempts.value[4] || 0) + 1
    store.recordEvent('challenge_error', 4, l4Task.value, { category: '代码拼图错误', ability_dim: 'SQL编程与优化' })
  }
}

function resetLevel4() {
  showModal.value = false
  const task = l4Tasks[l4Task.value]
  if (task) { task.pieces.forEach(p => p.used = false); task.slots.forEach(s => { s.filledPieceId = null; s.checked = false; s.correct = false }) }
  l4TaskSaved.value = 1; l4Task.value = 1
  l4Version.value++
}

// ===== Level 5: Flow Chart =====
interface L5Node { id: string; label: string; x: number; y: number; type: 'action' | 'decision' | 'start' | 'end' }
interface L5Connection { from: string; to: string }

const l5Task = ref(1)
const l5TaskSaved = ref(1)
const l5SelectedNode = ref<string | null>(null)
const l5Connections = ref<Record<number, L5Connection[]>>({ 1: [], 2: [] })

const l5TaskDefs: Record<number, { nodes: L5Node[]; expectedConnections: string[]; desc: string }> = {
  1: {
    desc: '新用户注册时，触发器自动为其开户并生成银行卡号。请按执行顺序连线：从INSERT开始，到生成卡号结束。',
    nodes: [
      { id: 'n5-1-1', label: 'INSERT新用户', x: 100, y: 200, type: 'start' },
      { id: 'n5-1-2', label: '触发器触发', x: 280, y: 200, type: 'action' },
      { id: 'n5-1-3', label: '生成随机卡号', x: 460, y: 200, type: 'action' },
      { id: 'n5-1-4', label: '检查卡号唯一', x: 460, y: 340, type: 'decision' },
      { id: 'n5-1-5', label: 'INSERT新卡', x: 640, y: 200, type: 'end' },
      { id: 'n5-1-6', label: '重新生成', x: 640, y: 340, type: 'action' },
    ],
    expectedConnections: ['n5-1-1→n5-1-2', 'n5-1-2→n5-1-3', 'n5-1-3→n5-1-4', 'n5-1-4→n5-1-5', 'n5-1-4→n5-1-6', 'n5-1-6→n5-1-3'],
  },
  2: {
    desc: 'John向Jane转账500元，使用事务保证原子性。请按执行顺序连线，包含异常回滚路径。',
    nodes: [
      { id: 'n5-2-1', label: 'BEGIN事务', x: 100, y: 200, type: 'start' },
      { id: 'n5-2-2', label: 'INSERT支取记录', x: 280, y: 200, type: 'action' },
      { id: 'n5-2-3', label: 'INSERT存入记录', x: 460, y: 200, type: 'action' },
      { id: 'n5-2-4', label: '余额是否足够', x: 460, y: 340, type: 'decision' },
      { id: 'n5-2-5', label: 'COMMIT提交', x: 640, y: 200, type: 'end' },
      { id: 'n5-2-6', label: 'ROLLBACK回滚', x: 640, y: 340, type: 'end' },
    ],
    expectedConnections: ['n5-2-1→n5-2-4', 'n5-2-4→n5-2-2', 'n5-2-2→n5-2-3', 'n5-2-3→n5-2-5', 'n5-2-4→n5-2-6'],
  },
}

const l5CurrentNodes = computed(() => l5TaskDefs[l5Task.value]?.nodes || [])
const l5CurrentDesc = computed(() => l5TaskDefs[l5Task.value]?.desc || '')
const l5CurrentConnections = computed(() => {
  const conns = l5Connections.value[l5Task.value] || []
  const nodes = l5TaskDefs[l5Task.value]?.nodes || []
  return conns.map(c => {
    const fromNode = nodes.find(n => n.id === c.from)
    const toNode = nodes.find(n => n.id === c.to)
    return { from: fromNode?.label || c.from, to: toNode?.label || c.to }
  })
})
const l5CurrentLines = computed(() => {
  const conns = l5Connections.value[l5Task.value] || []
  const nodes = l5TaskDefs[l5Task.value]?.nodes || []
  return conns.map(c => {
    const from = nodes.find(n => n.id === c.from)
    const to = nodes.find(n => n.id === c.to)
    if (!from || !to) return { x1: 0, y1: 0, x2: 0, y2: 0 }
    const dx = to.x - from.x, dy = to.y - from.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    const offset = 30
    return { x1: from.x + dx / dist * offset, y1: from.y + dy / dist * offset, x2: to.x - dx / dist * offset, y2: to.y - dy / dist * offset }
  })
})

function onL5NodeClick(node: L5Node) {
  if (!l5SelectedNode.value) { l5SelectedNode.value = node.id; return }
  if (l5SelectedNode.value === node.id) { l5SelectedNode.value = null; return }
  const conns = l5Connections.value[l5Task.value] || []
  const exists = conns.some(c => c.from === l5SelectedNode.value && c.to === node.id)
  if (!exists) {
    if (!l5Connections.value[l5Task.value]) l5Connections.value[l5Task.value] = []
    l5Connections.value[l5Task.value].push({ from: l5SelectedNode.value, to: node.id })
  }
  l5SelectedNode.value = null
}

function removeL5Connection(idx: number) {
  l5Connections.value[l5Task.value]?.splice(idx, 1)
}

function checkLevel5() {
  const def = l5TaskDefs[l5Task.value]
  if (!def) return
  const conns = l5Connections.value[l5Task.value] || []
  const connStrs = conns.map(c => `${c.from}→${c.to}`)
  const allCorrect = def.expectedConnections.every(ec => connStrs.includes(ec)) && connStrs.length === def.expectedConnections.length
  if (allCorrect) {
    if (l5Task.value < 2) {
      modalSuccess.value = true; showModal.value = true
      l5Task.value++; l5TaskSaved.value = l5Task.value
      applyPartialBoost(5, l5Task.value - 1, 2)
    } else {
      modalSuccess.value = true; showModal.value = true
      levelAttempts.value[5] = (levelAttempts.value[5] || 0) + 1
      if (!completedLevels.value.has(5)) {
        store.recordEvent('challenge_pass', 5, undefined, { attempts: levelAttempts.value[5] })
        applyBoost(5)
      }
    }
  } else {
    modalSuccess.value = false; showModal.value = true
    levelAttempts.value[5] = (levelAttempts.value[5] || 0) + 1
    store.recordEvent('challenge_error', 5, l5Task.value, { category: '流程连线错误', ability_dim: '数据库优化与调优' })
  }
}

function resetLevel5() {
  showModal.value = false
  l5Connections.value = { 1: [], 2: [] }
  l5SelectedNode.value = null
  l5TaskSaved.value = 1; l5Task.value = 1
}

// ===== Level 6: Performance Tuning (SQL Rewrite) =====
const l6Task = ref(1)
const l6TaskSaved = ref(1)
const l6Answer = ref('')
const l6Feedback = ref('')

interface L6TaskDef {
  query: string
  currentTime: string
  hint: string
  ref: string[]
  validate: (sql: string) => { correct: boolean; feedback?: string }
}

const l6Tasks: Record<number, L6TaskDef> = {
  1: {
    query: "SELECT * FROM tradeInfo\nWHERE tradeDate BETWEEN '2024-10-01' AND '2024-12-31';\n-- 交易表有百万级数据，按日期范围查询很慢",
    currentTime: '12.5s',
    hint: '使用CREATE TABLE ... PARTITION BY RANGE按tradeDate创建分区表，将数据按季度分区，查询时只扫描目标分区',
    ref: [
      '-- 示例：创建分区表',
      'CREATE TABLE sales_log (',
      '  id SERIAL,',
      '  sale_date DATE,',
      '  amount NUMERIC(10,2)',
      ') PARTITION BY RANGE(sale_date);',
      '',
      'CREATE TABLE sales_log_q1 PARTITION OF sales_log',
      "  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');",
    ],
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasPartition = s.includes('PARTITION') && (s.includes('RANGE') || s.includes('LIST'))
      const hasCreateTable = s.includes('CREATE TABLE')
      const hasTradeInfo = s.includes('TRADEINFO') || s.includes('TRADE_INFO')
      if (!hasCreateTable) return { correct: false, feedback: '请使用CREATE TABLE创建分区表' }
      if (!hasPartition) return { correct: false, feedback: '需要使用PARTITION BY子句指定分区方式' }
      if (!hasTradeInfo && !s.includes('PARTITION OF')) return { correct: false, feedback: '分区表应基于tradeInfo表结构' }
      return { correct: true }
    },
  },
  2: {
    query: "SELECT * FROM cardInfo WHERE customerID = 5;\n-- 银行卡表数据量大，按客户编号查询慢",
    currentTime: '3.2s',
    hint: '在customerID列上创建B-tree索引，加速等值查询',
    ref: [
      '-- 示例：创建索引',
      'CREATE INDEX idx_user_name ON userInfo(customerName);',
      '',
      '-- 示例：创建唯一索引',
      'CREATE UNIQUE INDEX idx_card_id ON cardInfo(cardID);',
    ],
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasCreateIndex = s.includes('CREATE INDEX') || s.includes('CREATE UNIQUE INDEX')
      const hasCustomerID = s.includes('CUSTOMERID')
      if (!hasCreateIndex) return { correct: false, feedback: '请使用CREATE INDEX创建索引' }
      if (!hasCustomerID) return { correct: false, feedback: '索引应建立在customerID列上' }
      return { correct: true }
    },
  },
  3: {
    query: "SELECT t1.a FROM t1 WHERE t1.a IN\n  (SELECT b FROM t2 WHERE t2.a = t1.a);\n-- 相关子查询，每行都要执行子查询，性能差",
    currentTime: '8.7s',
    hint: '将相关子查询改写为JOIN或非相关子查询，消除t2.a = t1.a的关联条件',
    ref: [
      '-- 示例：相关子查询改写为JOIN',
      'SELECT t1.a FROM t1',
      '  JOIN t2 ON t1.a = t2.b;',
      '',
      '-- 示例：改写为非相关子查询',
      "SELECT t1.a FROM t1 WHERE t1.a IN",
      "  (SELECT b FROM t2 WHERE t2.b > 0);",
    ],
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasJoin = s.includes('JOIN')
      const hasNonCorrelated = s.includes('IN') && s.includes('SELECT') && !s.includes('T2.A = T1.A') && !s.includes('T2.A=T1.A')
      if (!hasJoin && !hasNonCorrelated) return { correct: false, feedback: '请将相关子查询改写为JOIN或非相关子查询，消除t2.a=t1.a关联' }
      return { correct: true }
    },
  },
}

const l6CurrentTask = computed(() => l6Tasks[l6Task.value] || { query: '', currentTime: '', hint: '', ref: [], validate: () => ({ correct: false }) })

function checkLevel6Task() {
  const task = l6Tasks[l6Task.value]
  if (!task) return
  const result = task.validate(l6Answer.value)
  if (result.correct) {
    if (l6Task.value < 3) {
      modalSuccess.value = true; showModal.value = true
      l6Task.value++; l6TaskSaved.value = l6Task.value
      applyPartialBoost(6, l6Task.value - 1, 3)
      l6Answer.value = ''; l6Feedback.value = ''
    } else {
      modalSuccess.value = true; showModal.value = true
      levelAttempts.value[6] = (levelAttempts.value[6] || 0) + 1
      if (!completedLevels.value.has(6)) {
        store.recordEvent('challenge_pass', 6, undefined, { attempts: levelAttempts.value[6] })
        applyBoost(6)
      }
    }
  } else {
    modalSuccess.value = false
    l6Feedback.value = result.feedback || ''
    showModal.value = true
    levelAttempts.value[6] = (levelAttempts.value[6] || 0) + 1
    store.recordEvent('challenge_error', 6, l6Task.value, { category: 'SQL优化错误', ability_dim: '数据库优化与调优' })
  }
}

function resetLevel6() {
  showModal.value = false
  l6Task.value = 1; l6TaskSaved.value = 1
  l6Answer.value = ''; l6Feedback.value = ''
}

// ===== Level 7: Security & Permissions (Fill-in-blank) =====
const l7Part = ref(1)
const l7ActiveBlank = ref<number | null>(null)
const l7PartSaved = ref(1)

interface L7BlankState { filled: boolean; value: string; checked: boolean; correct: boolean }
const l7Blanks = ref<Record<number, L7BlankState>>({})

interface L7BlankMeta { mode: 'select' | 'input'; answer: string; options?: string[]; hint?: string }
const l7BlankMeta: Record<number, L7BlankMeta> = {
  0: { mode: 'select', answer: 'ROLE', options: ['USER', 'ROLE', 'GROUP', 'PROFILE'] },
  1: { mode: 'input', answer: 'CREATEROLE', hint: '创建角色的属性关键字' },
  2: { mode: 'select', answer: 'GRANT', options: ['GRANT', 'GIVE', 'ALLOW', 'PERMIT'] },
  3: { mode: 'input', answer: 'TO', hint: '授权给谁用什么介词' },
  4: { mode: 'select', answer: 'SELECT', options: ['READ', 'SELECT', 'VIEW', 'FETCH'] },
  5: { mode: 'input', answer: 'ON', hint: '指定操作对象的关键字' },
  6: { mode: 'select', answer: 'REVOKE', options: ['REMOVE', 'REVOKE', 'DENY', 'DELETE'] },
  7: { mode: 'input', answer: 'FROM', hint: '从谁那里回收权限' },
  8: { mode: 'select', answer: 'AUDIT', options: ['LOG', 'AUDIT', 'TRACE', 'MONITOR'] },
  9: { mode: 'input', answer: 'PASSWORD', hint: '修改密码的关键字' },
  10: { mode: 'select', answer: 'LOCK', options: ['BLOCK', 'LOCK', 'FREEZE', 'STOP'] },
  11: { mode: 'input', answer: 'FAILED_LOGIN_ATTEMPTS', hint: '设置登录失败次数限制的参数名' },
}

const l7PartLines: Record<number, Seg[][]> = {
  1: [
    [{ type: 'text', value: '-- 步骤1: 创建安全管理员角色' }],
    [{ type: 'text', value: 'CREATE ' }, { type: 'blank', blankId: 0 }, { type: 'text', value: ' security_admin ' }, { type: 'blank', blankId: 1 }, { type: 'text', value: ' PASSWORD \'Sec@1234\';' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤2: 创建只读用户' }],
    [{ type: 'text', value: 'CREATE USER readonly_user PASSWORD \'Read@1234\';' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤3: 将角色赋予用户' }],
    [{ type: 'text', value: 'GRANT security_admin ' }, { type: 'blank', blankId: 1 }, { type: 'text', value: ' readonly_user;' }],
  ],
  2: [
    [{ type: 'text', value: '-- 步骤4: 授予表查询权限' }],
    [{ type: 'blank', blankId: 2 }, { type: 'text', value: ' ' }, { type: 'blank', blankId: 4 }, { type: 'text', value: ' ' }, { type: 'blank', blankId: 5 }, { type: 'text', value: ' userInfo ' }, { type: 'blank', blankId: 3 }, { type: 'text', value: ' readonly_user;' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤5: 授予视图查询权限' }],
    [{ type: 'text', value: 'GRANT SELECT ON vw_userInfo TO readonly_user;' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤6: 授予存储过程执行权限' }],
    [{ type: 'text', value: 'GRANT EXECUTE ON PROCEDURE search_balance TO readonly_user;' }],
  ],
  3: [
    [{ type: 'text', value: '-- 步骤7: 回收查询权限' }],
    [{ type: 'blank', blankId: 6 }, { type: 'text', value: ' SELECT ON userInfo ' }, { type: 'blank', blankId: 7 }, { type: 'text', value: ' readonly_user;' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤8: 开启审计策略' }],
    [{ type: 'text', value: 'CREATE ' }, { type: 'blank', blankId: 8 }, { type: 'text', value: ' POLICY audit_login ON LOGIN;' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤9: 修改用户密码' }],
    [{ type: 'text', value: 'ALTER USER readonly_user ' }, { type: 'blank', blankId: 9 }, { type: 'text', value: " 'NewPass@5678';" }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤10: 锁定异常账户' }],
    [{ type: 'text', value: 'ALTER USER suspicious_user ACCOUNT ' }, { type: 'blank', blankId: 10 }, { type: 'text', value: ';' }],
    [{ type: 'text', value: '' }],
    [{ type: 'text', value: '-- 步骤11: 设置登录失败锁定策略' }],
    [{ type: 'text', value: 'ALTER USER readonly_user ' }, { type: 'blank', blankId: 11 }, { type: 'text', value: ' 5 PASSWORD_LOCK_TIME 2;' }],
  ],
}

function getL7PartBlankIds(part: number): number[] {
  const ids: number[] = []
  const lines = l7PartLines[part]
  if (!lines) return ids
  for (const line of lines) { for (const seg of line) { if (seg.type === 'blank') ids.push(seg.blankId) } }
  return ids
}

const l7CurrentLines = computed(() => l7PartLines[l7Part.value] || [])
const l7CurrentOptions = computed(() => {
  if (l7ActiveBlank.value === null) return []
  const meta = l7BlankMeta[l7ActiveBlank.value]
  if (!meta || meta.mode !== 'select') return []
  return meta.options || []
})

function initL7Blanks() {
  const b: Record<number, L7BlankState> = {}
  for (const id of Object.keys(l7BlankMeta)) { b[Number(id)] = { filled: false, value: '', checked: false, correct: false } }
  l7Blanks.value = b
  l7ActiveBlank.value = null
  l7Part.value = 1
}

function onL7Input(blankId: number, val: string) {
  l7Blanks.value[blankId] = { filled: val.trim().length > 0, value: val.trim(), checked: false, correct: false }
}

function selectL7Option(opt: string) {
  if (l7ActiveBlank.value === null) return
  l7Blanks.value[l7ActiveBlank.value] = { filled: true, value: opt, checked: false, correct: false }
}

function checkLevel7Part() {
  const ids = getL7PartBlankIds(l7Part.value)
  let allCorrect = true
  for (const id of ids) {
    const b = l7Blanks.value[id]
    const answer = l7BlankMeta[id].answer
    if (!b || !b.filled || b.value.toUpperCase() !== answer.toUpperCase()) {
      allCorrect = false
      l7Blanks.value[id] = { filled: b?.filled || false, value: b?.value || '', checked: true, correct: false }
    } else {
      l7Blanks.value[id] = { ...b, checked: true, correct: true }
    }
  }
  if (allCorrect) {
    if (l7Part.value < 3) {
      modalSuccess.value = true; showModal.value = true
      l7Part.value++; l7PartSaved.value = l7Part.value
      applyPartialBoost(7, l7Part.value - 1, 3)
    } else {
      modalSuccess.value = true; showModal.value = true
      levelAttempts.value[7] = (levelAttempts.value[7] || 0) + 1
      if (!completedLevels.value.has(7)) {
        store.recordEvent('challenge_pass', 7, undefined, { attempts: levelAttempts.value[7] })
        applyBoost(7)
      }
    }
  } else {
    modalSuccess.value = false; showModal.value = true
    levelAttempts.value[7] = (levelAttempts.value[7] || 0) + 1
    store.recordEvent('challenge_error', 7, l7Part.value, { category: '安全SQL填空错误', ability_dim: 'openGauss运维' })
  }
}

function resetLevel7() {
  showModal.value = false
  initL7Blanks()
  l7PartSaved.value = 1
}

// ===== Level 8: Backup & Restore (Code Puzzle) =====
interface L8Piece { id: string; text: string; used: boolean }
interface L8Slot { id: string; hint: string; expectedPieceId: string; filledPieceId: string | null; checked: boolean; correct: boolean }

const l8Task = ref(1)
const l8TaskSaved = ref(1)
const l8Version = ref(0)
let l8DraggedPieceId: string | null = null

const l8Tasks: Record<number, { pieces: L8Piece[]; slots: L8Slot[] }> = {
  1: {
    pieces: [
      { id: 'p8-1-2', text: 'gs_dump -U omm -W password -p 5432', used: false },
      { id: 'p8-1-5', text: '-F c', used: false },
      { id: 'p8-1-1', text: '-- 步骤1: 确认数据库状态正常', used: false },
      { id: 'p8-1-6', text: '-f /backup/bankdb.dump', used: false },
      { id: 'p8-1-3', text: '-d bankdb', used: false },
      { id: 'p8-1-4', text: '-t userInfo -t cardInfo', used: false },
    ],
    slots: [
      { id: 's8-1-1', hint: '1. 检查状态', expectedPieceId: 'p8-1-1', filledPieceId: null, checked: false, correct: false },
      { id: 's8-1-2', hint: '2. gs_dump命令', expectedPieceId: 'p8-1-2', filledPieceId: null, checked: false, correct: false },
      { id: 's8-1-3', hint: '3. 指定数据库', expectedPieceId: 'p8-1-3', filledPieceId: null, checked: false, correct: false },
      { id: 's8-1-4', hint: '4. 指定导出表', expectedPieceId: 'p8-1-4', filledPieceId: null, checked: false, correct: false },
      { id: 's8-1-5', hint: '5. 指定格式', expectedPieceId: 'p8-1-5', filledPieceId: null, checked: false, correct: false },
      { id: 's8-1-6', hint: '6. 指定输出文件', expectedPieceId: 'p8-1-6', filledPieceId: null, checked: false, correct: false },
    ],
  },
  2: {
    pieces: [
      { id: 'p8-2-1', text: 'gs_restore -U omm -W password -p 5432', used: false },
      { id: 'p8-2-4', text: '-d bankdb_new', used: false },
      { id: 'p8-2-2', text: '-C', used: false },
      { id: 'p8-2-5', text: '/backup/bankdb.dump', used: false },
      { id: 'p8-2-3', text: '-F c', used: false },
    ],
    slots: [
      { id: 's8-2-1', hint: '1. gs_restore命令', expectedPieceId: 'p8-2-1', filledPieceId: null, checked: false, correct: false },
      { id: 's8-2-2', hint: '2. 创建数据库', expectedPieceId: 'p8-2-2', filledPieceId: null, checked: false, correct: false },
      { id: 's8-2-3', hint: '3. 指定格式', expectedPieceId: 'p8-2-3', filledPieceId: null, checked: false, correct: false },
      { id: 's8-2-4', hint: '4. 指定目标数据库', expectedPieceId: 'p8-2-4', filledPieceId: null, checked: false, correct: false },
      { id: 's8-2-5', hint: '5. 指定备份文件', expectedPieceId: 'p8-2-5', filledPieceId: null, checked: false, correct: false },
    ],
  },
}

const l8CurrentPieces = computed(() => { void l8Version.value; const task = l8Tasks[l8Task.value]; return task ? [...task.pieces] : [] })
const l8CurrentSlots = computed(() => { void l8Version.value; const task = l8Tasks[l8Task.value]; return task ? [...task.slots] : [] })

function l8GetPieceText(pieceId: string): string {
  for (const task of Object.values(l8Tasks)) { const p = task.pieces.find(pp => pp.id === pieceId); if (p) return p.text }
  return ''
}

function onL8DragStart(_e: DragEvent, piece: L8Piece) { l8DraggedPieceId = piece.id }
function onL8Drop(_e: DragEvent, slot: L8Slot) {
  if (!l8DraggedPieceId) return
  const task = l8Tasks[l8Task.value]; if (!task) return
  const piece = task.pieces.find(p => p.id === l8DraggedPieceId)
  if (!piece || piece.used) return
  if (slot.filledPieceId) { const prev = task.pieces.find(p => p.id === slot.filledPieceId); if (prev) prev.used = false }
  piece.used = true; slot.filledPieceId = piece.id; slot.checked = false
  l8DraggedPieceId = null; l8Version.value++
}

function checkLevel8() {
  const task = l8Tasks[l8Task.value]; if (!task) return
  if (!task.slots.every(s => s.filledPieceId)) { modalSuccess.value = false; showModal.value = true; return }
  const allCorrect = task.slots.every(s => { const ok = s.filledPieceId === s.expectedPieceId; s.checked = true; s.correct = ok; return ok })
  l8Version.value++
  if (allCorrect) {
    if (l8Task.value < 2) {
      modalSuccess.value = true; showModal.value = true
      l8Task.value++; l8TaskSaved.value = l8Task.value
      applyPartialBoost(8, l8Task.value - 1, 2)
    } else {
      modalSuccess.value = true; showModal.value = true
      levelAttempts.value[8] = (levelAttempts.value[8] || 0) + 1
      if (!completedLevels.value.has(8)) {
        store.recordEvent('challenge_pass', 8, undefined, { attempts: levelAttempts.value[8] })
        applyBoost(8)
      }
    }
  } else {
    modalSuccess.value = false; showModal.value = true
    levelAttempts.value[8] = (levelAttempts.value[8] || 0) + 1
    store.recordEvent('challenge_error', 8, l8Task.value, { category: '备份恢复步骤错误', ability_dim: 'openGauss运维' })
  }
}

function resetLevel8() {
  showModal.value = false
  const task = l8Tasks[l8Task.value]
  if (task) { task.pieces.forEach(p => p.used = false); task.slots.forEach(s => { s.filledPieceId = null; s.checked = false; s.correct = false }) }
  l8TaskSaved.value = 1; l8Task.value = 1; l8Version.value++
}

// ===== Level 9: Bug Hunter (SQL Fix) =====
const l9Task = ref(1)
const l9TaskSaved = ref(1)
const l9Answer = ref('')
const l9Feedback = ref('')

interface L9TaskDef {
  bugHint: string
  buggyCode: string[]
  validate: (sql: string) => { correct: boolean; feedback?: string }
}

const l9Tasks: Record<number, L9TaskDef> = {
  1: {
    bugHint: '建表语句中数据类型与约束有2处错误',
    buggyCode: [
      'CREATE TABLE deposit (',
      '  savingID  CHAR PRIMARY KEY,',
      '  savingName VARCHAR(20) NOT NULL,',
      '  descrip VARCHAR(50)',
      ');',
    ],
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasSerial = s.includes('SERIAL') || s.includes('INT') || s.includes('INTEGER')
      const hasSavingID = s.includes('SAVINGID')
      if (!hasSavingID) return { correct: false, feedback: '请保留savingID列' }
      if (!hasSerial) return { correct: false, feedback: 'savingID应为SERIAL或INTEGER自增类型，不能用CHAR' }
      return { correct: true }
    },
  },
  2: {
    bugHint: '视图创建语句中AS和SELECT的位置有误',
    buggyCode: [
      'CREATE VIEW vw_cardInfo',
      'SELECT',
      '  cardID AS "卡号",',
      '  balance AS "余额"',
      'FROM cardInfo;',
    ],
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasAs = s.includes('AS') && s.indexOf('AS') < s.indexOf('SELECT')
      if (!s.includes('CREATE VIEW')) return { correct: false, feedback: '请保留CREATE VIEW语句' }
      if (!hasAs && !s.match(/CREATE\s+VIEW\s+\w+\s+AS\s+SELECT/)) return { correct: false, feedback: '视图名和SELECT之间缺少AS关键字' }
      return { correct: true }
    },
  },
  3: {
    bugHint: '存储过程中变量声明和语句顺序有误',
    buggyCode: [
      'CREATE OR REPLACE PROCEDURE search_balance',
      '(p_cardid CHAR(19))',
      'BEGIN',
      '  v_balance NUMERIC(18,2);',
      '  SELECT balance INTO v_balance FROM cardInfo',
      '    WHERE cardID = p_cardid;',
      '  RAISE NOTICE \'余额为：%元\', v_balance;',
      'END;',
    ],
    validate(sql: string) {
      const s = sql.replace(/\s+/g, ' ').trim().toUpperCase()
      const hasAs = s.includes('AS') && (s.indexOf('AS') < s.indexOf('BEGIN') || s.indexOf('AS') < s.indexOf('V_BALANCE'))
      if (!s.includes('CREATE') || !s.includes('PROCEDURE')) return { correct: false, feedback: '请保留CREATE PROCEDURE语句' }
      if (!hasAs) return { correct: false, feedback: '参数列表和BEGIN之间缺少AS关键字' }
      if (s.indexOf('V_BALANCE') < s.indexOf('BEGIN')) return { correct: false, feedback: '变量声明应在BEGIN之前（AS和BEGIN之间）' }
      return { correct: true }
    },
  },
}

const l9CurrentTask = computed(() => l9Tasks[l9Task.value] || { bugHint: '', buggyCode: [], validate: () => ({ correct: false }) })

function checkLevel9Task() {
  const task = l9Tasks[l9Task.value]; if (!task) return
  const result = task.validate(l9Answer.value)
  if (result.correct) {
    if (l9Task.value < 3) {
      modalSuccess.value = true; showModal.value = true
      l9Task.value++; l9TaskSaved.value = l9Task.value
      applyPartialBoost(9, l9Task.value - 1, 3)
      l9Answer.value = ''; l9Feedback.value = ''
    } else {
      modalSuccess.value = true; showModal.value = true
      levelAttempts.value[9] = (levelAttempts.value[9] || 0) + 1
      if (!completedLevels.value.has(9)) {
        store.recordEvent('challenge_pass', 9, undefined, { attempts: levelAttempts.value[9] })
        applyBoost(9)
      }
    }
  } else {
    modalSuccess.value = false; l9Feedback.value = result.feedback || ''
    showModal.value = true
    levelAttempts.value[9] = (levelAttempts.value[9] || 0) + 1
    store.recordEvent('challenge_error', 9, l9Task.value, { category: 'Bug修正错误', ability_dim: 'SQL编程与优化' })
  }
}

function resetLevel9() {
  showModal.value = false
  l9Task.value = 1; l9TaskSaved.value = 1
  l9Answer.value = ''; l9Feedback.value = ''
}

initL2Blanks()

onMounted(async () => {
  await store.fetchProfile()
  if (store.profile?.ability_scores) {
    const scores = store.profile.ability_scores as Record<string, number>
    abilities.value = abilityDims.map(dim => scores[dim] ?? 10)
  }
})
</script>

<style scoped>
.level-select { max-width: 800px; margin: 0 auto; }
.ability-section { margin-top: 32px; text-align: center; padding: 24px; background: #f8fafc; border-radius: 12px; border: 1px solid var(--border); }
.ability-header { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 12px; }
.ability-title { font-size: 18px; font-weight: 700; color: #1e293b; }
.ability-score-badge { font-size: 14px; color: #3b82f6; font-weight: 600; background: #eff6ff; padding: 4px 12px; border-radius: 20px; }
.radar-svg-main { width: 280px; height: 280px; }
.level-title { font-size: 22px; font-weight: 700; margin-bottom: 24px; text-align: center; }
.level-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.level-card { padding: 24px 20px; border: 2px solid var(--border); border-radius: 12px; cursor: pointer; transition: all 0.2s; text-align: center; }
.level-card.active { border-color: var(--primary); background: #f0f7ff; }
.level-card.completed { border-color: #86efac; background: #f0fdf4; }
.level-card.active:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(26,115,232,0.15); }
.level-card.locked { opacity: 0.5; cursor: not-allowed; }
.level-num { font-size: 13px; color: var(--primary); font-weight: 600; margin-bottom: 8px; }
.level-name { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
.level-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5; }
.level-difficulty { font-size: 12px; color: var(--text-secondary); }
.level-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.level-info { flex: 1; display: flex; align-items: center; gap: 10px; }
.level-badge { display: inline-block; background: var(--primary); color: white; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 4px; }
.level-label { font-size: 16px; font-weight: 600; }
.level-actions { display: flex; gap: 8px; }
.level-hint { background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 16px; line-height: 1.6; color: #92400e; }

.er-workspace { display: flex; gap: 20px; height: calc(100vh - var(--header-height) - 180px); min-height: 500px; }
.er-canvas-wrapper { flex: 1; overflow: auto; background: white; border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.er-canvas { width: 100%; height: 100%; min-width: 800px; min-height: 600px; background: #fafbfc; border-radius: 8px; }
.slot-area { cursor: pointer; }
.slot-area:hover rect, .slot-area:hover ellipse, .slot-area:hover polygon { stroke: #3b82f6; stroke-dasharray: none; }

.er-pieces { width: 200px; flex-shrink: 0; display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.pieces-header { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text); }
.pieces-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }

.piece-card { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border: 2px solid var(--border); border-radius: 8px; cursor: grab; transition: all 0.15s; }
.piece-card:hover { transform: translateX(-3px); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.piece-card:active { cursor: grabbing; }
.piece-card.used { opacity: 0.25; cursor: not-allowed; pointer-events: none; }
.piece-card.rect { border-color: #93c5fd; background: #eff6ff; }
.piece-card.ellipse { border-color: #86efac; background: #f0fdf4; }
.piece-card.diamond { border-color: #fcd34d; background: #fffbeb; }
.piece-shape-icon { width: 24px; text-align: center; font-size: 16px; color: var(--text-secondary); }
.piece-info { flex: 1; }
.piece-label { font-size: 14px; font-weight: 600; color: var(--text); }
.piece-type { font-size: 11px; color: var(--text-secondary); }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center; padding-top: 1vh; }
.ref-modal { background: white; border-radius: 12px; padding: 20px; width: 90vw; max-width: 1100px; max-height: 85vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
.ref-modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 16px; font-weight: 600; }
.ref-close { background: none; border: none; font-size: 22px; cursor: pointer; color: var(--text-secondary); padding: 0 4px; }
.ref-svg { width: 100%; max-width: 1060px; border-radius: 8px; border: 1px solid var(--border); background: #fafbfc; }

.modal-box { background: white; border-radius: 16px; padding: 32px 40px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.2); min-width: 300px; }
.modal-box.success { border: 2px solid #86efac; }
.modal-box.fail { border: 2px solid #fca5a5; }
.modal-icon { font-size: 48px; margin-bottom: 16px; }
.modal-text { font-size: 17px; font-weight: 600; margin-bottom: 24px; }
.modal-box.success .modal-text { color: #166534; }
.modal-box.fail .modal-text { color: #991b1b; }

.intro-modal { background: white; border-radius: 12px; padding: 24px; width: 720px; max-width: 90vw; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
.intro-modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-size: 18px; font-weight: 700; }
.intro-body { display: flex; gap: 24px; }
.intro-left { flex: 1; }
.intro-right { width: 300px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.intro-section { margin-bottom: 16px; }
.intro-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
.intro-text { font-size: 14px; line-height: 1.7; color: var(--text); }
.intro-skills { display: flex; flex-wrap: wrap; gap: 6px; }
.intro-skill-tag { display: inline-block; padding: 3px 10px; background: #dbeafe; color: #1d4ed8; font-size: 12px; font-weight: 600; border-radius: 4px; }
.intro-score { font-size: 28px; font-weight: 700; color: var(--primary); }
.intro-start-btn { width: 100%; margin-top: 8px; padding: 10px; font-size: 15px; }
.radar-svg { width: 100%; max-width: 280px; }

.sql-workspace { display: flex; gap: 20px; height: calc(100vh - var(--header-height) - 240px); min-height: 400px; }
.sql-terminal { flex: 1; display: flex; flex-direction: column; background: #1e1e2e; border-radius: 10px; overflow: hidden; border: 1px solid #313244; }
.terminal-header { display: flex; align-items: center; gap: 8px; padding: 10px 16px; background: #181825; }
.terminal-dot { width: 12px; height: 12px; border-radius: 50%; }
.terminal-dot.red { background: #f38ba8; }
.terminal-dot.yellow { background: #f9e2af; }
.terminal-dot.green { background: #a6e3a1; }
.terminal-title { font-size: 12px; color: #6c7086; margin-left: 8px; }
.terminal-body { flex: 1; padding: 16px; overflow-y: auto; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 13px; line-height: 1.7; }
.sql-line { white-space: pre; }
.sql-text { color: #cdd6f4; }
.sql-blank { display: inline-block; min-width: 60px; padding: 1px 8px; border-bottom: 2px dashed #6c7086; color: #6c7086; cursor: pointer; text-align: center; transition: all 0.15s; border-radius: 3px; }
.sql-blank:hover { border-color: #89b4fa; background: rgba(137,180,250,0.1); }
.sql-blank.filled { color: #89b4fa; border-bottom-style: solid; border-color: #89b4fa; }
.sql-blank.correct { color: #a6e3a1; border-color: #a6e3a1; background: rgba(166,227,161,0.1); }
.sql-blank.wrong { color: #f38ba8; border-color: #f38ba8; background: rgba(243,139,168,0.1); }
.sql-input { display: inline-block; min-width: 80px; max-width: 140px; padding: 1px 6px; border: none; border-bottom: 2px dashed #6c7086; background: rgba(137,180,250,0.08); color: #89b4fa; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 13px; text-align: center; outline: none; border-radius: 2px; }
.sql-input::placeholder { color: #585b70; font-size: 11px; }
.sql-input:focus { border-bottom-color: #89b4fa; background: rgba(137,180,250,0.15); }
.sql-input.correct { border-bottom-style: solid; border-color: #a6e3a1; color: #a6e3a1; background: rgba(166,227,161,0.1); }
.sql-input.wrong { border-bottom-style: solid; border-color: #f38ba8; color: #f38ba8; background: rgba(243,139,168,0.1); }

.l2-progress { margin-bottom: 16px; }
.l2-progress-bar { height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-bottom: 8px; }
.l2-progress-fill { height: 100%; background: var(--primary); border-radius: 3px; transition: width 0.3s; }
.l2-progress-steps { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); }
.l2-progress-steps span { padding: 2px 8px; border-radius: 4px; }
.l2-progress-steps span.done { color: #16a34a; font-weight: 600; }
.l2-progress-steps span.current { color: var(--primary); font-weight: 600; background: #f0f7ff; }

.sql-options { width: 220px; flex-shrink: 0; display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.options-header { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text); }
.options-target { font-size: 13px; color: var(--primary); font-weight: 600; margin-bottom: 10px; padding: 6px 10px; background: #f0f7ff; border-radius: 6px; text-align: center; }
.options-hint { font-size: 13px; color: var(--text-secondary); margin-bottom: 10px; text-align: center; }
.options-list { display: flex; flex-direction: column; gap: 8px; }
.option-btn { padding: 10px 14px; border: 2px solid var(--border); border-radius: 8px; background: white; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; text-align: center; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; }
.option-btn:hover { border-color: var(--primary); background: #f0f7ff; }
.option-btn.selected { border-color: var(--primary); background: #dbeafe; color: var(--primary); }

.l3-workspace { display: flex; gap: 20px; height: calc(100vh - var(--header-height) - 280px); min-height: 380px; }
.l3-ref-panel { width: 45%; display: flex; flex-direction: column; background: #1e1e2e; border-radius: 10px; overflow: hidden; border: 1px solid #313244; }
.l3-editor-panel { flex: 1; display: flex; flex-direction: column; background: #1e1e2e; border-radius: 10px; overflow: hidden; border: 1px solid #313244; }
.l3-panel-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; background: #181825; font-size: 13px; font-weight: 600; color: #cdd6f4; }
.l3-divider { border: none; border-top: 1px solid #45475a; margin: 16px 0; }
.l3-task-text { color: #a6adc8; font-size: 20px; line-height: 1.8; white-space: pre-wrap; }
.l3-ref-body { flex: 1; padding: 16px; overflow-y: auto; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 13px; line-height: 1.8; }
.l3-ref-line { white-space: pre; color: #cdd6f4; }
.l3-ref-line:empty { height: 1.8em; }
.l3-editor { flex: 1; padding: 16px; background: transparent; border: none; color: #89b4fa; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 13px; line-height: 1.8; resize: none; outline: none; }
.l3-editor::placeholder { color: #585b70; }

.l4-workspace { display: flex; gap: 20px; height: calc(100vh - var(--header-height) - 280px); min-height: 380px; }
.l4-pieces-panel { width: 38%; display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.l4-slots-panel { flex: 1; display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.l4-panel-header { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text); }
.l4-pieces-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.l4-piece { padding: 10px 14px; border: 2px solid var(--border); border-radius: 8px; cursor: grab; transition: all 0.15s; background: #f8fafc; }
.l4-piece:hover { border-color: var(--primary); background: #f0f7ff; transform: translateX(-3px); }
.l4-piece:active { cursor: grabbing; }
.l4-piece.used { opacity: 0.25; cursor: not-allowed; pointer-events: none; }
.l4-piece code { font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 13px; color: #1e293b; white-space: pre-wrap; }
.l4-slots-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.l4-slot { padding: 10px 14px; border: 2px dashed var(--border); border-radius: 8px; min-height: 44px; display: flex; align-items: center; transition: all 0.15s; background: #fafbfc; }
.l4-slot:hover { border-color: #93c5fd; background: #f0f7ff; }
.l4-slot.filled { border-style: solid; border-color: #93c5fd; background: #eff6ff; }
.l4-slot.correct { border-color: #86efac; background: #f0fdf4; }
.l4-slot.wrong { border-color: #fca5a5; background: #fef2f2; }
.l4-slot-text { font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 13px; color: #1e293b; white-space: pre-wrap; }
.l4-slot-placeholder { font-size: 13px; color: #94a3b8; }

.l5-workspace { display: flex; gap: 20px; height: calc(100vh - var(--header-height) - 280px); min-height: 380px; }
.l5-canvas { flex: 1; background: #fafbfc; border: 1px solid var(--border); border-radius: 10px; }
.l5-node-rect { cursor: pointer; transition: all 0.15s; }
.l5-node-rect:hover { filter: brightness(0.95); }
.l5-info-panel { width: 240px; flex-shrink: 0; display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.l5-panel-header { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text); }
.l5-task-desc { font-size: 13px; line-height: 1.7; color: var(--text); margin-bottom: 16px; }
.l5-connections { flex: 1; overflow-y: auto; }
.l5-conn-header { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px; }
.l5-conn-item { display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: #f0f7ff; border-radius: 6px; font-size: 12px; color: #1e293b; margin-bottom: 6px; }
.l5-conn-del { background: none; border: none; color: #ef4444; cursor: pointer; font-size: 16px; padding: 0 4px; }
.l5-conn-empty { font-size: 13px; color: #94a3b8; text-align: center; margin-top: 24px; }

.l6-workspace { display: flex; gap: 20px; height: calc(100vh - var(--header-height) - 280px); min-height: 380px; }
.l6-scenario-panel { width: 45%; display: flex; flex-direction: column; background: #1e1e2e; border-radius: 10px; overflow: hidden; border: 1px solid #313244; }
.l6-options-panel { flex: 1; display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.l6-panel-header { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text); }
.l6-scenario-panel .l6-panel-header { padding: 10px 16px; background: #181825; color: #cdd6f4; margin-bottom: 0; }
.l6-scenario-body { flex: 1; padding: 16px; overflow-y: auto; }
.l6-query { font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 13px; line-height: 1.8; color: #cdd6f4; white-space: pre-wrap; margin-bottom: 20px; padding: 12px; background: #181825; border-radius: 8px; }
.l6-metrics { display: flex; gap: 16px; }
.l6-metric { display: flex; flex-direction: column; align-items: center; padding: 12px 20px; background: #181825; border-radius: 8px; }
.l6-metric-label { font-size: 12px; color: #6c7086; margin-bottom: 6px; }
.l6-metric-value { font-size: 22px; font-weight: 700; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; }
.l6-slow { color: #f38ba8; }
.l6-fast { color: #a6e3a1; }
.l6-options-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
.l6-option { padding: 14px 16px; border: 2px solid var(--border); border-radius: 10px; cursor: pointer; transition: all 0.15s; }
.l6-option:hover { border-color: var(--primary); background: #f0f7ff; }
.l6-option.selected { border-color: var(--primary); background: #dbeafe; }
.l6-option-title { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px; }
.l6-option-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }

.l6-scenario-block { margin-bottom: 16px; }
.l6-scenario-label { font-size: 12px; color: #6c7086; font-weight: 600; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.l6-query-display { font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 12px; line-height: 1.7; color: #cdd6f4; white-space: pre-wrap; background: #181825; padding: 10px; border-radius: 6px; }
.l6-time-slow { font-size: 22px; font-weight: 700; color: #f38ba8; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; }
.l6-hint-text { font-size: 13px; line-height: 1.7; color: #a6adc8; }
.l9-bug-hint { font-size: 14px; color: #f38ba8; font-weight: 600; margin-bottom: 12px; padding: 8px 12px; background: rgba(243,139,168,0.1); border-radius: 6px; border-left: 3px solid #f38ba8; }
.l9-divider { border: none; border-top: 1px solid #45475a; margin: 12px 0; }
</style>