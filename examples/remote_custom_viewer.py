import argparse
from typing import Tuple

from aitviewer.remote.message import Message

# For simplicity in this example we have the client and server code in the same
# script and run the client or the server depending on the --server command line flag.
#
# In practice the custom viewer could be in a different script,
# potentially already running in an other process or on a remote host.
parser = argparse.ArgumentParser()
parser.add_argument(
    "--server", help="run the viewer part of the script, if not given run the client instead", action="store_true"
)
args = parser.parse_args()

# We define a custom message identifier that we will send to our custom viewer.
#
# The Message class is just an enumeration of message identifiers with integer type.
# All values greater than or equal to Message.USER_MESSAGE are not used internally by the viewer
# and can be safely used to send custom messages.
CUSTOM_MESSAGE = Message.USER_MESSAGE

# Run the server or the viewer depending on the command line argument.
if not args.server:
    #
    # Client script sending data to the remote viewer.
    #

    import time

    import trimesh

    from aitviewer.remote.renderables.meshes import RemoteMeshes
    from aitviewer.remote.viewer import RemoteViewer

    cube = trimesh.load("resources/cube.obj")

    # Create a viewer in a separate process, passing a path to the script
    # and a command line argument.
    #
    # This will invoke the script with the following command:
    #   python path/to/script.py --server
    v = RemoteViewer.create_new_process([__file__, "--server"])

    # Send 3 Meshes to the viewer
    for i in range(3):
        RemoteMeshes(
            v,
            cube.vertices,
            cube.faces,
            name=f"Cube {i}",
            position=(i, 0, 0),
            scale=0.1,
            flat_shading=True,
        )
        time.sleep(1)

    # Send a custom message to the viewer, we specify
    # the message type and a keyword argument that will
    # be sent to the viewer's 'process_message()' method.
    v.send_message(CUSTOM_MESSAGE, index=1)

else:
    #
    # Server script running the custom viewer.
    #

    from aitviewer.configuration import CONFIG as C
    from aitviewer.remote.message import Message
    from aitviewer.viewer import Viewer

    cubes = []

    # We inherit from the Viewer class to override the 'process_message()' method.
    class CustomViewer(Viewer):
        # This function is called on the viewer every time a new message has to
        # be processed. By overriding this method we can intercept messages before
        # they are sent to the viewer and add custom functionality to them.
        def process_message(self, type: Message, remote_uid: int, args: list, kwargs: dict, client: Tuple[str, str]):
            if type != CUSTOM_MESSAGE:
                # If we didn't receive a custom message we first forward
                # it to the viewer to make sure it's handled normally.
                super().process_message(type, remote_uid, args, kwargs, client)

                # remote_uid is an id generated by the client to reference
                # remote nodes that it created. This value is sent to the viewer
                # on every message to identify which node it applies to.
                # The viewer keeps track of the mapping from remote_uid and client
                # to the local uid of the node. When a message to create a new node is
                # processed by the viewer, an entry is added to this map.
                #
                # The client parameter is a tuple (ip, port) that can be used to identify
                # the client that sent the message. This is mostly useful when multiple
                # client are communicating with the viewer and it can be ignored otherwise.
                #
                # We can use this helper function to recover the node that was
                # created by the message we just received and the viewer just processed.
                cube = self.get_node_by_remote_uid(remote_uid, client)
                cubes.append(cube)

                # We select the cube just created and center the view on it.
                self.scene.select(cube)
                self.center_view_on_selection()
            else:
                # Extract the 'index' keyword argument from the arguments passed
                # to 'send_message()' by the client.
                index = kwargs["index"]

                # We use this to select one of the cubes and center the view on it.
                self.scene.select(cubes[index])
                self.center_view_on_selection()

    # Create the viewer. Overriding the default configuration to ensure that
    # the viewer is listening for incoming connections.
    C.update_conf({"server_enabled": True})
    v = CustomViewer()
    v.scene.floor.enabled = False
    v.scene.camera.position = (1, 1, 1)
    v.run()
