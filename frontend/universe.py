import streamlit.components.v1 as components

def inject_universe():
    components.html("""
        <script>
            const parentDoc = window.parent.document;
            if (!parentDoc.getElementById('universe-canvas')) {
                const script = parentDoc.createElement('script');
                script.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js";
                script.onload = () => {
                    // Create Canvas
                    const canvas = parentDoc.createElement('canvas');
                    canvas.id = 'universe-canvas';
                    canvas.style.position = 'fixed';
                    canvas.style.top = '0';
                    canvas.style.left = '0';
                    canvas.style.width = '100vw';
                    canvas.style.height = '100vh';
                    canvas.style.zIndex = '-999';
                    canvas.style.pointerEvents = 'none';
                    parentDoc.body.appendChild(canvas);
                    
                    // Create Logic Script
                    const logicScript = parentDoc.createElement('script');
                    logicScript.innerHTML = `
                        const canvas = document.getElementById('universe-canvas');
                        const scene = new THREE.Scene();
                        // Deep space background color
                        scene.background = new THREE.Color(0x050510);
                        
                        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
                        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
                        renderer.setSize(window.innerWidth, window.innerHeight);
                        renderer.setPixelRatio(window.devicePixelRatio);
                        
                        // Lighting
                        const ambient = new THREE.AmbientLight(0xffffff, 0.4);
                        scene.add(ambient);
                        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
                        dirLight.position.set(10, 10, 10);
                        scene.add(dirLight);
                        
                        // 3D Logo (Sphere + Orbiting Surfaces)
                        const logoGroup = new THREE.Group();
                        
                        // Core (Blue Sphere)
                        const coreGeo = new THREE.SphereGeometry(1.2, 32, 32);
                        const coreMat = new THREE.MeshStandardMaterial({ 
                            color: 0x22d3ee, 
                            emissive: 0x0891b2,
                            emissiveIntensity: 0.5,
                            roughness: 0.2,
                            metalness: 0.8
                        });
                        const core = new THREE.Mesh(coreGeo, coreMat);
                        logoGroup.add(core);
                        
                        // Internal Light to make the core glow
                        const pointLight = new THREE.PointLight(0x22d3ee, 2, 20);
                        logoGroup.add(pointLight);
                        
                        // Outer Surfaces
                        // Creating curved shells using SphereGeometry with sweep angles
                        const shellGeo = new THREE.SphereGeometry(2.5, 32, 32, 0, Math.PI * 0.8, Math.PI/4, Math.PI/2);
                        
                        const shellMat1 = new THREE.MeshStandardMaterial({ 
                            color: 0x6366f1, // Indigo
                            side: THREE.DoubleSide, 
                            roughness: 0.3,
                            metalness: 0.6,
                            transparent: true,
                            opacity: 0.95
                        });
                        const shell1 = new THREE.Mesh(shellGeo, shellMat1);
                        
                        const shellMat2 = new THREE.MeshStandardMaterial({ 
                            color: 0x1e1b4b, // Deep dark purple/blue
                            side: THREE.DoubleSide, 
                            roughness: 0.3,
                            metalness: 0.6,
                            transparent: true,
                            opacity: 0.95
                        });
                        const shell2 = new THREE.Mesh(shellGeo, shellMat2);
                        shell2.rotation.y = Math.PI; // Opposite side
                        
                        // Tilt the shells slightly for better 3D effect
                        shell1.rotation.z = Math.PI / 6;
                        shell2.rotation.z = Math.PI / 6;
                        
                        logoGroup.add(shell1);
                        logoGroup.add(shell2);
                        scene.add(logoGroup);
                        
                        // Particles (Stars)
                        const particlesCount = 2000;
                        const particlesGeo = new THREE.BufferGeometry();
                        const posArray = new Float32Array(particlesCount * 3);
                        const initialPosArray = new Float32Array(particlesCount * 3);
                        const sizesArray = new Float32Array(particlesCount);
                        
                        for(let i = 0; i < particlesCount * 3; i++) {
                            // Spread in a large volume
                            let v = (Math.random() - 0.5) * 60;
                            posArray[i] = v;
                            initialPosArray[i] = v;
                        }
                        
                        for(let i = 0; i < particlesCount; i++) {
                            // Uneven sizes
                            sizesArray[i] = Math.random() * 2.5 + 0.5;
                        }
                        
                        particlesGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
                        particlesGeo.setAttribute('initialPosition', new THREE.BufferAttribute(initialPosArray, 3));
                        particlesGeo.setAttribute('size', new THREE.BufferAttribute(sizesArray, 1));
                        
                        // Custom shader material for sizing particles
                        const particleMat = new THREE.ShaderMaterial({
                            uniforms: {
                                time: { value: 0 }
                            },
                            vertexShader: \`
                                attribute float size;
                                varying vec3 vPosition;
                                void main() {
                                    vPosition = position;
                                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                                    gl_PointSize = size * (30.0 / -mvPosition.z);
                                    gl_Position = projectionMatrix * mvPosition;
                                }
                            \`,
                            fragmentShader: \`
                                void main() {
                                    // Circular particle
                                    float r = distance(gl_PointCoord, vec2(0.5));
                                    if (r > 0.5) discard;
                                    gl_FragColor = vec4(1.0, 1.0, 1.0, 0.8 - r);
                                }
                            \`,
                            transparent: true,
                            blending: THREE.AdditiveBlending,
                            depthWrite: false
                        });
                        
                        const particlesMesh = new THREE.Points(particlesGeo, particleMat);
                        scene.add(particlesMesh);
                        
                        camera.position.z = 15;
                        
                        // Interaction variables
                        let mouseX = 0;
                        let mouseY = 0;
                        
                        document.addEventListener('mousemove', (event) => {
                            // Normalize mouse coords to -1 to +1
                            mouseX = (event.clientX / window.innerWidth) * 2 - 1;
                            mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
                        });
                        
                        const clock = new THREE.Clock();
                        
                        function animate() {
                            requestAnimationFrame(animate);
                            const elapsedTime = clock.getElapsedTime();
                            
                            // Rotate logo in slow motion
                            logoGroup.rotation.y = elapsedTime * 0.2;
                            logoGroup.rotation.x = Math.sin(elapsedTime * 0.1) * 0.3;
                            
                            // Rotate universe slightly
                            particlesMesh.rotation.y = elapsedTime * 0.03;
                            particlesMesh.rotation.z = elapsedTime * 0.01;
                            
                            // Repel logic
                            // Map mouse coordinates to rough 3D space at z=0 plane
                            // Camera z is 15, FOV is 60. Height at z=0 is approx 15 * tan(30deg) * 2 = ~17.3
                            // Width is Height * aspect
                            const aspect = window.innerWidth / window.innerHeight;
                            const targetY = mouseY * 8.65;
                            const targetX = mouseX * 8.65 * aspect;
                            
                            const positions = particlesGeo.attributes.position.array;
                            const initials = particlesGeo.attributes.initialPosition.array;
                            
                            // Transform mouse target to local coordinates of particlesMesh
                            // Since particlesMesh is rotating, we approximate by keeping targets in world space
                            // and treating particles in world space. But particles are child of scene.
                            
                            for(let i=0; i<particlesCount; i++) {
                                let ix = initials[i*3];
                                let iy = initials[i*3+1];
                                let iz = initials[i*3+2];
                                
                                let px = positions[i*3];
                                let py = positions[i*3+1];
                                let pz = positions[i*3+2];
                                
                                // Reverse particlesMesh rotation for mouse calculation
                                // Actually, simpler to calculate distance directly. The universe is swirling,
                                // the cursor is static on screen. Let's just repel based on current screen-ish space.
                                let dx = px - targetX;
                                let dy = py - targetY;
                                
                                // Only repel if z is close to 0 (foreground stars)
                                let dz = pz;
                                let dist = Math.sqrt(dx*dx + dy*dy + dz*dz*0.1); // weaken z effect
                                
                                const repelRadius = 4.0;
                                if (dist < repelRadius && dist > 0.1) {
                                    let force = (repelRadius - dist) / repelRadius;
                                    positions[i*3] += (dx / dist) * force * 0.2;
                                    positions[i*3+1] += (dy / dist) * force * 0.2;
                                } else {
                                    // Smoothly return to initial positions
                                    positions[i*3] += (ix - px) * 0.02;
                                    positions[i*3+1] += (iy - py) * 0.02;
                                    positions[i*3+2] += (iz - pz) * 0.02;
                                }
                            }
                            particlesGeo.attributes.position.needsUpdate = true;
                            
                            renderer.render(scene, camera);
                        }
                        
                        animate();
                        
                        window.addEventListener('resize', () => {
                            camera.aspect = window.innerWidth / window.innerHeight;
                            camera.updateProjectionMatrix();
                            renderer.setSize(window.innerWidth, window.innerHeight);
                        });
                    `;
                    parentDoc.body.appendChild(logicScript);
                };
                parentDoc.head.appendChild(script);
            }
        </script>
    """, height=0)
