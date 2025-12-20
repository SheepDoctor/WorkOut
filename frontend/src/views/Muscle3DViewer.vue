<template>
  <div class="muscle-3d-viewer">
    <div class="info-panel max-w-sm">
      <div class="mb-6">
        <router-link to="/" class="text-blue-400 text-xs font-bold uppercase tracking-widest mb-4 inline-flex items-center hover:underline pointer-events-auto">
          <i class="fa-solid fa-arrow-left mr-2"></i> 返回主页
        </router-link>
        <h1 class="text-3xl font-black text-white tracking-tighter">ANATOMY<span class="text-blue-500">PRO</span></h1>
        <p class="text-slate-400 text-xs mt-1 uppercase tracking-widest font-bold">专业健身肌肉 3D 映射系统</p>
      </div>
      
      <div id="muscle-details" class="transition-all duration-500 opacity-0 translate-y-4">
        <div class="p-5 bg-slate-900/80 rounded-xl border border-slate-700/50 backdrop-blur-xl shadow-2xl">
          <div class="stats-badge" id="muscle-category">核心肌群</div>
          <h2 id="muscle-name" class="text-2xl font-bold text-white mb-2">---</h2>
          <p id="muscle-desc" class="text-slate-400 text-sm leading-relaxed mb-4"></p>
          
          <div class="space-y-3">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <div class="w-1 h-3 bg-blue-500 rounded-full"></div>
                <span class="text-xs font-bold text-slate-300 uppercase">主要训练动作</span>
              </div>
              <p id="muscle-exercises" class="text-slate-100 text-sm font-medium"></p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="hover-label" class="muscle-label border-l-4 border-l-blue-500">
      <span id="label-text" class="font-bold text-white text-sm"></span>
    </div>

    <div class="controls-hint text-slate-300 flex items-center gap-4">
      <span>🖱️ <b>左键</b> 自由旋转</span>
      <div class="w-px h-3 bg-slate-600"></div>
      <span>🖱️ <b>右键</b> 平移模型</span>
      <div class="w-px h-3 bg-slate-600"></div>
      <span>🖱️ <b>滚轮</b> 细节缩放</span>
    </div>

    <div ref="canvasContainer" class="canvas-container"></div>
  </div>
</template>

<script>
import { onMounted, onBeforeUnmount, ref } from 'vue'

export default {
  name: 'Muscle3DViewer',
  setup() {
    const canvasContainer = ref(null)
    let scene, camera, renderer, raycaster, mouse
    let muscles = []
    let hoveredMuscle = null
    let modelGroup
    let animationId = null
    let isDragging = false
    let dragButton = 0 // 0: 左键, 2: 右键
    let previousMousePosition = { x: 0, y: 0 }

    // 扩展的肌肉数据
    const muscleData = {
      "chest": { name: "胸大肌", cat: "上肢前侧", desc: "位于胸廓前壁，是主要推类动作的核心。决定了胸部的厚度和轮廓。", exercises: "杠铃卧推、双杠臂屈伸、哑铃飞鸟" },
      "abs_upper": { name: "上腹肌", cat: "核心", desc: "负责身体的向前屈曲，是\"六块腹肌\"的主要视觉组成部分。", exercises: "仰卧起坐、卷腹" },
      "abs_lower": { name: "下腹肌", cat: "核心", desc: "控制骨盆后倾及下肢上抬，对腰椎稳定性至关重要。", exercises: "悬垂举腿、登山者" },
      "deltoid_l": { name: "左肩三角肌", cat: "上肢", desc: "包裹肩关节的厚实肌肉，分为前、中、后三束。", exercises: "侧平举、推举、面拉" },
      "deltoid_r": { name: "右肩三角肌", cat: "上肢", desc: "包裹肩关节的厚实肌肉，分为前、中、后三束。", exercises: "侧平举、推举、面拉" },
      "bicep_l": { name: "左肱二头肌", cat: "上肢", desc: "上臂前侧，负责手臂弯曲和前臂旋后。", exercises: "杠铃弯举、哑铃锤式弯举" },
      "bicep_r": { name: "右肱二头肌", cat: "上肢", desc: "上臂前侧，负责手臂弯曲和前臂旋后。", exercises: "杠铃弯举、哑铃锤式弯举" },
      "tricep_l": { name: "左肱三头肌", cat: "上肢", desc: "上臂后侧，占手臂体积的2/3，负责肘部伸展。", exercises: "绳索下压、窄握卧推" },
      "tricep_r": { name: "右肱三头肌", cat: "上肢", desc: "上臂后侧，占手臂体积的2/3，负责肘部伸展。", exercises: "绳索下压、窄握卧推" },
      "forearm_l": { name: "左前臂肌群", cat: "上肢", desc: "控制抓握力和手腕活动，是功能性力量的基础。", exercises: "农夫行走、腕弯举" },
      "forearm_r": { name: "右前臂肌群", cat: "上肢", desc: "控制抓握力和手腕活动，是功能性力量的基础。", exercises: "农夫行走、腕弯举" },
      "quad_l": { name: "左股四头肌", cat: "下肢", desc: "大腿前侧肌群，人体最有力的肌肉之一，负责伸膝。", exercises: "深蹲、倒蹬、腿屈伸" },
      "quad_r": { name: "右股四头肌", cat: "下肢", desc: "大腿前侧肌群，人体最有力的肌肉之一，负责伸膝。", exercises: "深蹲、倒蹬、腿屈伸" },
      "calf_l": { name: "左小腿肌(腓肠肌)", cat: "下肢", desc: "负责踝关节跖屈，对弹跳和爆发力至关重要。", exercises: "提踵" },
      "calf_r": { name: "右小腿肌(腓肠肌)", cat: "下肢", desc: "负责踝关节跖屈，对弹跳和爆发力至关重要。", exercises: "提踵" },
      "traps": { name: "斜方肌", cat: "背部", desc: "连接颈部和背部，负责肩胛骨的提升和稳定。", exercises: "耸肩、硬拉" },
      "lats": { name: "背阔肌", cat: "背部", desc: "身体最宽的肌肉，赋予身体\"V\"字轮廓。", exercises: "引体向上、划船" },
      "head": { name: "头部", cat: "神经中枢", desc: "保护大脑，包含面部表情肌和咀嚼肌。", exercises: "颈部静态抗阻" }
    }

    function init() {
      const THREE = window.THREE
      if (!THREE) {
        console.error('Three.js is not loaded')
        return
      }

      scene = new THREE.Scene()
      scene.background = new THREE.Color(0x020617)
      
      camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000)
      camera.position.set(0, 1.2, 3.5)

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
      renderer.setSize(window.innerWidth, window.innerHeight)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      renderer.shadowMap.enabled = true
      canvasContainer.value.appendChild(renderer.domElement)

      raycaster = new THREE.Raycaster()
      mouse = new THREE.Vector2()

      // 增强光照：三点式照明 + 边缘光
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
      scene.add(ambientLight)

      const mainLight = new THREE.DirectionalLight(0xffffff, 0.8)
      mainLight.position.set(2, 4, 5)
      mainLight.castShadow = true
      scene.add(mainLight)

      const rimLight = new THREE.PointLight(0x3b82f6, 1.5)
      rimLight.position.set(-3, 2, -3)
      scene.add(rimLight)

      const fillLight = new THREE.DirectionalLight(0x60a5fa, 0.3)
      fillLight.position.set(-5, 0, 2)
      scene.add(fillLight)

      modelGroup = new THREE.Group()
      createRealisticHuman()
      scene.add(modelGroup)

      // 辅助线网格
      const grid = new THREE.GridHelper(10, 20, 0x1e293b, 0x0f172a)
      grid.position.y = -1
      scene.add(grid)

      // 鼠标事件
      window.addEventListener('mousemove', onMouseMove)
      window.addEventListener('resize', onWindowResize)
      
      renderer.domElement.addEventListener('mousedown', (e) => {
        if(e.button === 0 || e.button === 2) {
          isDragging = true
          dragButton = e.button
        }
      })
      window.addEventListener('mouseup', () => {
        isDragging = false
        dragButton = 0
      })
      // 阻止右键菜单
      renderer.domElement.addEventListener('contextmenu', (e) => {
        e.preventDefault()
      })
      window.addEventListener('mousemove', handleMouseMove)

      // 滚轮缩放
      window.addEventListener('wheel', (e) => {
        camera.position.z = Math.max(2, Math.min(6, camera.position.z + e.deltaY * 0.005))
      })

      animate()
    }

    function createRealisticHuman() {
      const THREE = window.THREE
      // 基础材质
      const bodyMat = new THREE.MeshStandardMaterial({ 
        color: 0x334155, 
        metalness: 0.1, 
        roughness: 0.7,
        emissive: 0x000000
      })
      
      const createMuscle = (geo, pos, scale, rot, id) => {
        const mesh = new THREE.Mesh(geo, bodyMat.clone())
        mesh.position.set(...pos)
        mesh.scale.set(...scale)
        if(rot) mesh.rotation.set(...rot)
        mesh.userData.id = id
        mesh.castShadow = true
        mesh.receiveShadow = true
        modelGroup.add(mesh)
        muscles.push(mesh)
        return mesh
      }

      // 1. 头部 (Head)
      createMuscle(new THREE.SphereGeometry(0.14, 32, 24), [0, 1.75, 0], [0.9, 1.1, 1], null, "head")

      // 2. 脖子与斜方肌 (Traps)
      createMuscle(new THREE.CylinderGeometry(0.06, 0.15, 0.2), [0, 1.6, 0], [1.5, 1, 0.8], null, "traps")

      // 3. 躯干 - 胸部 (Chest)
      createMuscle(new THREE.BoxGeometry(0.5, 0.3, 0.2), [0, 1.42, 0.1], [1, 1, 1], [0.1, 0, 0], "chest")

      // 4. 躯干 - 腹肌 (Abs)
      createMuscle(new THREE.BoxGeometry(0.38, 0.2, 0.18), [0, 1.2, 0.08], [1, 1, 1], null, "abs_upper")
      createMuscle(new THREE.BoxGeometry(0.35, 0.2, 0.16), [0, 1.0, 0.06], [1, 1, 1], null, "abs_lower")

      // 5. 背部 - 背阔肌 (Lats)
      createMuscle(new THREE.BoxGeometry(0.6, 0.5, 0.15), [0, 1.35, -0.08], [1, 1, 1], [0.1, 0, 0], "lats")

      // 6. 肩部 (Deltoids)
      const shoulderGeo = new THREE.SphereGeometry(0.12, 16, 16)
      createMuscle(shoulderGeo, [-0.35, 1.52, 0.05], [1.1, 1.3, 1.1], null, "deltoid_l")
      createMuscle(shoulderGeo, [0.35, 1.52, 0.05], [1.1, 1.3, 1.1], null, "deltoid_r")

      // 7. 上臂 - 二头肌/三头肌 (Arms)
      const upperArmGeo = new THREE.CylinderGeometry(0.07, 0.06, 0.45, 16)
      createMuscle(upperArmGeo, [-0.42, 1.25, 0.05], [1.2, 1, 1.2], [0, 0, 0.1], "bicep_l")
      createMuscle(upperArmGeo, [0.42, 1.25, 0.05], [1.2, 1, 1.2], [0, 0, -0.1], "bicep_r")
      
      // 8. 前臂 (Forearms)
      const forearmGeo = new THREE.CylinderGeometry(0.06, 0.04, 0.45, 16)
      createMuscle(forearmGeo, [-0.48, 0.85, 0.05], [1, 1, 1], [0, 0, 0.05], "forearm_l")
      createMuscle(forearmGeo, [0.48, 0.85, 0.05], [1, 1, 1], [0, 0, -0.05], "forearm_r")

      // 9. 大腿 (Quads)
      const thighGeo = new THREE.CylinderGeometry(0.14, 0.1, 0.75, 16)
      createMuscle(thighGeo, [-0.18, 0.5, 0], [1.1, 1, 1.2], [0, 0, 0.05], "quad_l")
      createMuscle(thighGeo, [0.18, 0.5, 0], [1.1, 1, 1.2], [0, 0, -0.05], "quad_r")

      // 10. 小腿 (Calves)
      const calfGeo = new THREE.CylinderGeometry(0.1, 0.05, 0.7, 16)
      createMuscle(calfGeo, [-0.22, -0.2, 0], [0.9, 1, 0.9], null, "calf_l")
      createMuscle(calfGeo, [0.22, -0.2, 0], [0.9, 1, 0.9], null, "calf_r")
    }

    function onMouseMove(event) {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1

      const label = document.getElementById('hover-label')
      if (label) {
        label.style.left = (event.clientX + 20) + 'px'
        label.style.top = (event.clientY + 20) + 'px'
      }
    }

    function handleMouseMove(e) {
      if(isDragging && modelGroup) {
        const deltaMove = {
          x: e.offsetX - previousMousePosition.x,
          y: e.offsetY - previousMousePosition.y
        }
        
        if (dragButton === 0) {
          // 左键：左右旋转（Y轴）
          modelGroup.rotation.y += deltaMove.x * 0.007
        } else if (dragButton === 2) {
          // 右键：上下平移（Y轴位置）
          modelGroup.position.y -= deltaMove.y * 0.01
          // 限制上下移动范围
          modelGroup.position.y = Math.max(-1, Math.min(2, modelGroup.position.y))
        }
      }
      previousMousePosition = { x: e.offsetX, y: e.offsetY }
    }

    function onWindowResize() {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    }

    function animate() {
      animationId = requestAnimationFrame(animate)

      if (raycaster && camera && muscles.length > 0) {
        raycaster.setFromCamera(mouse, camera)
        const intersects = raycaster.intersectObjects(muscles)

        const detailsPanel = document.getElementById('muscle-details')
        const label = document.getElementById('hover-label')

        if (intersects.length > 0) {
          const object = intersects[0].object
          
          if (hoveredMuscle !== object) {
            if (hoveredMuscle) {
              hoveredMuscle.material.color.setHex(0x334155)
              hoveredMuscle.material.emissive.setHex(0x000000)
              hoveredMuscle.scale.multiplyScalar(0.95)
            }
            
            hoveredMuscle = object
            hoveredMuscle.material.color.setHex(0x3b82f6)
            hoveredMuscle.material.emissive.setHex(0x1e40af)
            hoveredMuscle.scale.multiplyScalar(1.05)

            const data = muscleData[object.userData.id]
            if (data && detailsPanel) {
              const nameEl = document.getElementById('muscle-name')
              const catEl = document.getElementById('muscle-category')
              const descEl = document.getElementById('muscle-desc')
              const exercisesEl = document.getElementById('muscle-exercises')
              const labelTextEl = document.getElementById('label-text')
              
              if (nameEl) nameEl.innerText = data.name
              if (catEl) catEl.innerText = data.cat
              if (descEl) descEl.innerText = data.desc
              if (exercisesEl) exercisesEl.innerText = data.exercises
              if (labelTextEl) labelTextEl.innerText = data.name
              
              detailsPanel.style.opacity = "1"
              detailsPanel.style.transform = "translateY(0)"
              if (label) label.style.display = 'block'
            }
          }
        } else {
          if (hoveredMuscle) {
            hoveredMuscle.material.color.setHex(0x334155)
            hoveredMuscle.material.emissive.setHex(0x000000)
            hoveredMuscle.scale.multiplyScalar(1/1.05)
            hoveredMuscle = null
            
            if (detailsPanel) {
              detailsPanel.style.opacity = "0"
              detailsPanel.style.transform = "translateY(16px)"
            }
            if (label) label.style.display = 'none'
          }
        }
      }

      if (renderer && scene && camera) {
        renderer.render(scene, camera)
      }
    }

    function cleanup() {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('resize', onWindowResize)
      if (renderer && canvasContainer.value) {
        canvasContainer.value.removeChild(renderer.domElement)
        renderer.dispose()
      }
    }

    onMounted(() => {
      // 等待Three.js加载
      if (window.THREE) {
        init()
      } else {
        const checkThree = setInterval(() => {
          if (window.THREE) {
            clearInterval(checkThree)
            init()
          }
        }, 100)
      }
    })

    onBeforeUnmount(() => {
      cleanup()
    })

    return {
      canvasContainer
    }
  }
}
</script>

<style scoped>
.muscle-3d-viewer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #020617;
  color: white;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.canvas-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.canvas-container :deep(canvas) {
  display: block;
}

.info-panel {
  position: absolute;
  top: 24px;
  left: 24px;
  pointer-events: none;
  z-index: 20;
}

.muscle-label {
  position: absolute;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(56, 189, 248, 0.4);
  padding: 8px 12px;
  border-radius: 6px;
  backdrop-filter: blur(8px);
  display: none;
  pointer-events: none;
  z-index: 50;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.controls-hint {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(30, 41, 59, 0.6);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.75rem;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.1);
}

.stats-badge {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
  margin-bottom: 4px;
}
</style>

