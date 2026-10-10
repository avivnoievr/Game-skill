extends SceneTree

func _initialize():
    var args = OS.get_cmdline_user_args()
    if args.size() != 2:
        push_error("usage: godot --headless --path tests/pilot --script tests/pilot/control.gd -- MODEL.glb REPORT.json")
        quit(2)
        return
    var document = GLTFDocument.new()
    var state = GLTFState.new()
    var result = document.append_from_file(args[0], state)
    if result != OK:
        push_error("GLTF read failed: %s" % result)
        quit(1)
        return
    var scene = document.generate_scene(state)
    root.add_child(scene)
    await process_frame
    var rotor = scene.find_child("Rotor", true, false) as MeshInstance3D
    var base = scene.find_child("Base", true, false) as MeshInstance3D
    var guard = scene.find_child("Guard", true, false) as MeshInstance3D
    var socket = scene.find_child("SOCKET_cord", true, false) as Node3D
    if rotor == null or base == null or guard == null or socket == null:
        push_error("Required runtime nodes missing")
        quit(1)
        return
    var rotor_before = rotor.global_transform
    var base_before = base.global_transform
    var guard_before = guard.global_transform
    var socket_before = socket.global_transform
    var vertices = rotor.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
    var point_before = rotor.global_transform * vertices[0]
    rotor.rotate_object_local(Vector3(0, 0, -1), deg_to_rad(45))
    var point_after = rotor.global_transform * vertices[0]
    var checks = {
        "required_runtime_nodes": true,
        "rotor_origin_stationary": rotor.global_position.is_equal_approx(rotor_before.origin),
        "rotor_rotation_changed": not rotor.global_basis.is_equal_approx(rotor_before.basis),
        "rotor_vertex_moved": point_before.distance_to(point_after) > 0.001,
        "base_stationary": base.global_transform.is_equal_approx(base_before),
        "guard_stationary": guard.global_transform.is_equal_approx(guard_before),
        "socket_stationary": socket.global_transform.is_equal_approx(socket_before),
        "socket_expected_position": socket.global_position.is_equal_approx(Vector3(0, 0.025, -0.080))
    }
    var report = {"engine": Engine.get_version_info(), "checks": checks,
                  "rotor_vertex_displacement_m": point_before.distance_to(point_after),
                  "socket_position": [socket.global_position.x, socket.global_position.y, socket.global_position.z]}
    var output = FileAccess.open(args[1], FileAccess.WRITE)
    if output == null:
        push_error("Cannot write report")
        quit(2)
        return
    output.store_string(JSON.stringify(report, "  "))
    output.close()
    print("GODOT_PILOT_JSON " + JSON.stringify(report))
    for value in checks.values():
        if not value:
            quit(1)
            return
    quit(0)
