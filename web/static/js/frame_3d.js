/**
 * Basic 3D visualizer for a Frame's cabinets/drawers.
 *
 * Coordinate system (millimeters, matches apps/storage/models.py):
 *   X = right, Y = up, Z = depth (into the frame, away from the viewer).
 *   Origin is the Frame's own bottom-left-front corner.
 *   A cabinet's position_x/y/z is its minimum (bottom-left-front) corner.
 *
 * Nothing here is hardcoded: every box's position/size comes from the JSON
 * served by FrameVisualizationDataView. Drawer boxes are computed from their
 * cabinet's width/height split into that cabinet's column x row grid, using
 * each drawer's own column/row (its real stored position, not its id).
 */
(function () {
    "use strict";

    var SCALE = 1 / 100; // 100mm per Three.js unit.
    var CABINET_COLOR = 0x3558f6;
    var DRAWER_COLOR = 0x9fb0ff;
    var HIGHLIGHT_COLOR = 0xffb020;

    var container = document.getElementById("frame-3d-viewer");
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
        1000
    );
    camera.position.set(6, 6, 10);

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
    var selected = null;
    var pickables = [];

    function addBox(spec) {
        var geometry = new THREE.BoxGeometry(
            spec.width * SCALE,
            spec.height * SCALE,
            spec.depth * SCALE
        );
        var material = new THREE.MeshStandardMaterial({
            color: spec.color,
            transparent: !!spec.opacity,
            opacity: spec.opacity || 1,
        });
        var mesh = new THREE.Mesh(geometry, material);
        // spec.x/y/z mark the box's minimum corner; BoxGeometry is centered
        // on its local origin, so offset by half the box's size.
        mesh.position.set(
            (spec.x + spec.width / 2) * SCALE,
            (spec.y + spec.height / 2) * SCALE,
            (spec.z + spec.depth / 2) * SCALE
        );
        mesh.userData = Object.assign({ baseColor: spec.color }, spec.userData);
        scene.add(mesh);
        pickables.push(mesh);
        return mesh;
    }

    function buildScene(frame) {
        frame.cabinets.forEach(function (cabinet) {
            addBox({
                width: cabinet.dimensions.width,
                height: cabinet.dimensions.height,
                depth: cabinet.dimensions.depth,
                x: cabinet.position.x,
                y: cabinet.position.y,
                z: cabinet.position.z,
                color: CABINET_COLOR,
                opacity: 0.55,
                userData: {
                    kind: "cabinet",
                    name: "Cabinet " + cabinet.code,
                    position: cabinet.position,
                    drawerCount: cabinet.drawers.length,
                },
            });

            var columns = cabinet.grid.columns;
            var rows = cabinet.grid.rows;
            var cellWidth = cabinet.dimensions.width / columns;
            var cellHeight = cabinet.dimensions.height / rows;
            var gap = Math.min(cellWidth, cellHeight) * 0.08;

            // Drawers straddle the cabinet's front (max-Z, camera-facing) face
            // like real open drawer fronts, so they poke out past the solid
            // cabinet box instead of being hidden inside it.
            var drawerDepth = cabinet.dimensions.depth * 0.35;
            var drawerZ = cabinet.position.z + cabinet.dimensions.depth - drawerDepth / 2;

            cabinet.drawers.forEach(function (drawer) {
                var cellX = cabinet.position.x + (drawer.column - 1) * cellWidth;
                var cellY = cabinet.position.y + (drawer.row - 1) * cellHeight;
                addBox({
                    width: cellWidth - gap,
                    height: cellHeight - gap,
                    depth: drawerDepth,
                    x: cellX + gap / 2,
                    y: cellY + gap / 2,
                    z: drawerZ,
                    color: DRAWER_COLOR,
                    userData: {
                        kind: "drawer",
                        name: "Drawer " + drawer.code,
                        cabinetName: "Cabinet " + cabinet.code,
                        componentCount: drawer.component_count,
                        gridPosition: { column: drawer.column, row: drawer.row },
                    },
                });
            });
        });
    }

    function select(mesh) {
        if (selected) {
            selected.material.color.setHex(selected.userData.baseColor);
        }
        selected = mesh;
        if (!mesh) {
            selectedNameEl.textContent = "Nothing selected — click a cabinet or drawer";
            selectedDetailsEl.textContent = "";
            return;
        }
        mesh.material.color.setHex(HIGHLIGHT_COLOR);
        var d = mesh.userData;
        if (d.kind === "cabinet") {
            selectedNameEl.textContent = d.name;
            selectedDetailsEl.textContent =
                "Position: X " + d.position.x + " / Y " + d.position.y + " / Z " + d.position.z +
                " · " + d.drawerCount + " drawer(s)";
        } else {
            selectedNameEl.textContent = d.name;
            selectedDetailsEl.textContent =
                "Cabinet: " + d.cabinetName + " · Components: " + d.componentCount;
        }
    }

    renderer.domElement.addEventListener("click", function (event) {
        var rect = renderer.domElement.getBoundingClientRect();
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(pointer, camera);
        var intersects = raycaster.intersectObjects(pickables);
        select(intersects.length ? intersects[0].object : null);
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
        .then(function (frame) {
            buildScene(frame);
            animate();
        });
})();
