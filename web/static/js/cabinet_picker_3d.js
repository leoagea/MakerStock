/**
 * 3D cabinet placement picker for the "Add cabinet" form.
 *
 * Shows the frame's existing cabinets. Click any FACE of an existing cabinet
 * to snap the new cabinet flush against that face — the raycaster hit gives
 * us the exact face normal, so clicking the right face snaps right, the top
 * face snaps on top, the back face snaps behind, etc. This is what avoids
 * every new cabinet defaulting to the same spot and stacking on top of the
 * last one. A live ghost box previews the new cabinet's current form values
 * (updated as you edit width/height/depth/position), so you can see where
 * it'll land before saving. If the frame has no cabinets yet, the fields
 * already default to (0, 0, 0) — the frame's bottom-left-front corner — and
 * nothing further is needed.
 */
(function () {
    "use strict";

    var SCALE = 1 / 100; // matches frame_3d.js
    var CABINET_COLOR = 0x3558f6;
    var SELECTED_COLOR = 0xffb020;
    var GHOST_COLOR = 0x3ddc84;

    // Face normal (local/object space — our boxes are never rotated, only
    // translated, so local axes equal world axes) -> human-readable label.
    var FACE_LABELS = {
        "x+": "to the right of",
        "x-": "to the left of",
        "y+": "on top of",
        "y-": "below",
        "z+": "in front of",
        "z-": "behind",
    };

    var container = document.getElementById("cabinet-3d-picker");
    if (!container) {
        return;
    }

    var dataUrl = container.dataset.visualizationUrl;
    var hintEl = document.getElementById("cabinet-3d-picker-hint");

    var fieldIds = [
        "id_width",
        "id_height",
        "id_depth",
        "id_position_x",
        "id_position_y",
        "id_position_z",
    ];
    var fields = {};
    fieldIds.forEach(function (id) {
        fields[id] = document.getElementById(id);
    });

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
    var pickables = [];
    var selected = null;
    var ghost = null;

    function boxMesh(width, height, depth, x, y, z, color, opacity) {
        var geometry = new THREE.BoxGeometry(width * SCALE, height * SCALE, depth * SCALE);
        var material = new THREE.MeshStandardMaterial({
            color: color,
            transparent: opacity !== undefined,
            opacity: opacity === undefined ? 1 : opacity,
        });
        var mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(
            (x + width / 2) * SCALE,
            (y + height / 2) * SCALE,
            (z + depth / 2) * SCALE
        );
        return mesh;
    }

    function numberValue(id, fallback) {
        var el = fields[id];
        var value = el ? parseFloat(el.value) : NaN;
        return isNaN(value) ? fallback : value;
    }

    function updateGhost() {
        if (ghost) {
            scene.remove(ghost);
        }
        ghost = boxMesh(
            numberValue("id_width", 300),
            numberValue("id_height", 400),
            numberValue("id_depth", 250),
            numberValue("id_position_x", 0),
            numberValue("id_position_y", 0),
            numberValue("id_position_z", 0),
            GHOST_COLOR,
            0.45
        );
        var edges = new THREE.LineSegments(
            new THREE.EdgesGeometry(ghost.geometry),
            new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.6 })
        );
        ghost.add(edges);
        scene.add(ghost);
    }

    function buildScene(frame) {
        frame.cabinets.forEach(function (cabinet) {
            var mesh = boxMesh(
                cabinet.dimensions.width,
                cabinet.dimensions.height,
                cabinet.dimensions.depth,
                cabinet.position.x,
                cabinet.position.y,
                cabinet.position.z,
                CABINET_COLOR
            );
            mesh.userData = { cabinet: cabinet, baseColor: CABINET_COLOR };
            scene.add(mesh);
            pickables.push(mesh);
        });

        updateGhost();

        if (!frame.cabinets.length && hintEl) {
            hintEl.textContent =
                "No cabinets yet — this one will be placed at the frame's origin (bottom-left-front corner).";
        }
    }

    function clearSelection() {
        if (selected) {
            selected.material.color.setHex(selected.userData.baseColor);
        }
        selected = null;
    }

    function dominantFace(normal) {
        var ax = Math.abs(normal.x);
        var ay = Math.abs(normal.y);
        var az = Math.abs(normal.z);
        if (ax >= ay && ax >= az) {
            return { axis: "x", sign: normal.x > 0 ? 1 : -1 };
        }
        if (ay >= ax && ay >= az) {
            return { axis: "y", sign: normal.y > 0 ? 1 : -1 };
        }
        return { axis: "z", sign: normal.z > 0 ? 1 : -1 };
    }

    function snapToFace(mesh, faceNormal) {
        clearSelection();
        selected = mesh;
        mesh.material.color.setHex(SELECTED_COLOR);

        var c = mesh.userData.cabinet;
        var newWidth = numberValue("id_width", 300);
        var newHeight = numberValue("id_height", 400);
        var newDepth = numberValue("id_depth", 250);
        var face = dominantFace(faceNormal);

        var x = c.position.x;
        var y = c.position.y;
        var z = c.position.z;

        if (face.axis === "x") {
            x = face.sign > 0 ? c.position.x + c.dimensions.width : c.position.x - newWidth;
        } else if (face.axis === "y") {
            y = face.sign > 0 ? c.position.y + c.dimensions.height : c.position.y - newHeight;
        } else {
            z = face.sign > 0 ? c.position.z + c.dimensions.depth : c.position.z - newDepth;
        }

        if (fields.id_position_x) fields.id_position_x.value = x;
        if (fields.id_position_y) fields.id_position_y.value = y;
        if (fields.id_position_z) fields.id_position_z.value = z;

        if (hintEl) {
            var label = FACE_LABELS[face.axis + (face.sign > 0 ? "+" : "-")];
            hintEl.textContent = "Snapped " + label + " Cabinet " + c.code + ".";
        }
        updateGhost();
    }

    renderer.domElement.addEventListener("click", function (event) {
        var rect = renderer.domElement.getBoundingClientRect();
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(pointer, camera);
        var intersects = raycaster.intersectObjects(pickables);
        if (!intersects.length) {
            clearSelection();
            return;
        }
        var hit = intersects[0];
        snapToFace(hit.object, hit.face.normal);
    });

    fieldIds.forEach(function (id) {
        if (fields[id]) {
            fields[id].addEventListener("input", updateGhost);
        }
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
