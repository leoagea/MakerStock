/**
 * System-level 3D overview: one box per Frame, laid out left to right.
 * Each box is sized from that frame's real cabinet data (see
 * apps/storage/services.py: frame_bounding_box) — only the row layout
 * itself (left-to-right, fixed gap) is a display choice made here, not
 * physical data. Clicking a frame navigates to its own 3D view
 * (frame_3d.html), which shows its cabinets/drawers in full.
 */
(function () {
    "use strict";

    var SCALE = 1 / 100; // 100mm per Three.js unit, matches frame_3d.js.
    var GAP = 150; // mm between frames in this overview layout.
    var FRAME_COLOR = 0x3558f6;
    var HIGHLIGHT_COLOR = 0xffb020;

    var container = document.getElementById("system-3d-viewer");
    if (!container) {
        return;
    }

    var dataUrl = container.dataset.visualizationUrl;
    var selectedNameEl = document.querySelector("#viewer-3d-selected-name span");
    var selectedDetailsEl = document.getElementById("viewer-3d-selected-details");

    var scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111214);

    var camera = new THREE.PerspectiveCamera(
        50,
        container.clientWidth / container.clientHeight,
        0.1,
        2000
    );
    camera.position.set(8, 8, 14);

    var renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio || 1);
    container.appendChild(renderer.domElement);

    var controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    var directional = new THREE.DirectionalLight(0xffffff, 0.8);
    directional.position.set(5, 10, 7);
    scene.add(directional);

    var raycaster = new THREE.Raycaster();
    var pointer = new THREE.Vector2();
    var pickables = [];

    function addFrameBox(frame, x) {
        var d = frame.dimensions;
        var geometry = new THREE.BoxGeometry(d.width * SCALE, d.height * SCALE, d.depth * SCALE);
        var material = new THREE.MeshStandardMaterial({
            color: FRAME_COLOR,
            transparent: true,
            opacity: 0.5,
        });
        var mesh = new THREE.Mesh(geometry, material);
        mesh.position.set((x + d.width / 2) * SCALE, (d.height / 2) * SCALE, (d.depth / 2) * SCALE);
        mesh.userData = {
            baseColor: FRAME_COLOR,
            name: "Frame " + frame.code,
            cabinetCount: frame.cabinet_count,
            url: frame.url,
        };

        var edges = new THREE.LineSegments(
            new THREE.EdgesGeometry(geometry),
            new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.4 })
        );
        mesh.add(edges);

        scene.add(mesh);
        pickables.push(mesh);
        return mesh;
    }

    function buildScene(system) {
        var x = 0;
        system.frames.forEach(function (frame) {
            addFrameBox(frame, x);
            x += frame.dimensions.width + GAP;
        });
    }

    function showInfo(mesh) {
        if (!mesh) {
            selectedNameEl.textContent = "Nothing selected — click a frame to open it";
            selectedDetailsEl.textContent = "";
            return;
        }
        selectedNameEl.textContent = mesh.userData.name;
        selectedDetailsEl.textContent = mesh.userData.cabinetCount + " cabinet(s)";
    }

    renderer.domElement.addEventListener("click", function (event) {
        var rect = renderer.domElement.getBoundingClientRect();
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(pointer, camera);
        var intersects = raycaster.intersectObjects(pickables);
        if (!intersects.length) {
            showInfo(null);
            return;
        }
        var mesh = intersects[0].object;
        mesh.material.color.setHex(HIGHLIGHT_COLOR);
        showInfo(mesh);
        window.location.href = mesh.userData.url;
    });

    window.addEventListener("resize", function () {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }

    fetch(dataUrl)
        .then(function (response) {
            return response.json();
        })
        .then(function (system) {
            buildScene(system);
            animate();
        });
})();
