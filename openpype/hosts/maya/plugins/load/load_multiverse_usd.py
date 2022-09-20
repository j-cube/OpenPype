# -*- coding: utf-8 -*-
import maya.cmds as cmds
from maya import mel
import os

from openpype.pipeline import (
    load,
    get_representation_path
)
from openpype.hosts.maya.api.lib import (
    maintained_selection,
    namespaced,
    unique_namespace
)
from openpype.hosts.maya.api.pipeline import containerise
from openpype.client import get_representations, get_representation_by_id


class MultiverseUsdLoader(load.LoaderPlugin):
    """Read USD data in a Multiverse Compound"""

    families = ["model", "usd", "mvUsdComposition", "mvUsdOverride",
                "pointcache", "animation"]
    representations = ["usd", "usda", "usdc", "usdz", "abc"]

    label = "Load USD to Multiverse"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self, context, name=None, namespace=None, options=None):

        import traceback
        self.log.warning("MultiverseUsdLoader:load: >>>>>")
        for l in traceback.format_stack(): self.log.warning("    - {}".format(l))
        self.log.warning("MultiverseUsdLoader:load: <<<<<<")

        self.log.warning("MultiverseUsdLoader:load: \ncontext='{}'\nname='{}'\nnamespace='{}'\noptions='{}'"
            "".format(context,name,namespace,options))
        asset = context['asset']['name']
        namespace = namespace or unique_namespace(
            asset + "_",
            prefix="_" if asset[0].isdigit() else "",
            suffix="_",
        )
        self.log.warning("         : {}".format(namespace))

        # Create the shape
        cmds.loadPlugin("MultiverseForMaya", quiet=True)

        shape = None
        transform = None
        with maintained_selection():
            cmds.namespace(addNamespace=namespace)
            with namespaced(namespace, new=False):
                import multiverse
                shape = multiverse.CreateUsdCompound(self.fname)
                transform = cmds.listRelatives(
                    shape, parent=True, fullPath=True)[0]

                # Grab what is currently selected to restore it later
                previous_selection = cmds.ls(selection=True, dag=True, long=True)
                cmds.select(shape)
                cmds.addAttr(longName="OP_repr_path", dataType="string")
                attrib_name = "{}.OP_repr_path".format(shape)
                cmds.setAttr(attrib_name, self.fname, type="string")
                # restore selection
                cmds.select(previous_selection)

        nodes = [transform, shape]
        self[:] = nodes

        return containerise(
            name=name,
            namespace=namespace,
            nodes=nodes,
            context=context,
            loader=self.__class__.__name__)

    def update(self, container, representation):
        # type: (dict, dict) -> None
        """Update container with specified representation."""

        import traceback
        self.log.warning("MultiverseUsdLoader:update: >>>>>")
        for l in traceback.format_stack(): self.log.warning("    - {}".format(l))
        self.log.warning("MultiverseUsdLoader:update: <<<<<<")

        self.log.warning("MultiverseUsdLoader:update: NEW: \ncontainer='{}'\nrepresentation='{}'"
            "".format(container,representation))
        node = container['objectName']
        assert cmds.objExists(node), "Missing container"

        members = cmds.sets(node, query=True) or []
        shapes = cmds.ls(members, type="mvUsdCompoundShape")
        assert shapes, "Cannot find mvUsdCompoundShape in container"

        project_name = representation["context"]["project"]["name"]
        prev_representation_id = cmds.getAttr("{}.representation".format(node))
        prev_representation = get_representation_by_id(project_name,
                                                  prev_representation_id)
        prev_path = os.path.normpath(prev_representation["data"]["path"])

        cmds.loadPlugin("MultiverseForMaya", quiet=True)
        import multiverse

        for shape in shapes:

            asset_paths = multiverse.GetUsdCompoundAssetPaths(shape)
            asset_paths = [os.path.normpath(p) for p in asset_paths]
            self.log.warning("  :prev_path='{}'\n  :asset_paths='{}'"
                "".format(prev_path,asset_paths))
        
            assert asset_paths.count(prev_path) == 1, \
                "Couldn't find matching path (or too many)"
            prev_path_idx = asset_paths.index(prev_path)

            path = get_representation_path(representation)
            asset_paths[prev_path_idx] = path

            multiverse.SetUsdCompoundAssetPaths(shape, asset_paths)

        self.log.warning("Representation: '{}':'{}'"
            "".format("{}.representation".format(node),str(representation["_id"])))
        cmds.setAttr("{}.representation".format(node),
                     str(representation["_id"]),
                     type="string")
        mel.eval('refreshEditorTemplates;')

    def switch(self, container, representation):
        import traceback
        self.log.warning("MultiverseUsdLoader:switch: >>>>>")
        for l in traceback.format_stack(): self.log.warning("    - {}".format(l))
        self.log.warning("MultiverseUsdLoader:switch: <<<<<<")

        self.log.warning("MultiverseUsdLoader:switch: \ncontainer='{}'\nrepresentation='{}'"
            "".format(container,representation))
        self.update(container, representation)

    def remove(self, container):
        # type: (dict) -> None
        """Remove loaded container."""
        # Delete container and its contents
        self.log.warning("MultiverseUsdLoader:switch: \ncontainer='{}'"
            "".format(container))
        if cmds.objExists(container['objectName']):
            members = cmds.sets(container['objectName'], query=True) or []
            cmds.delete([container['objectName']] + members)

        # Remove the namespace, if empty
        namespace = container['namespace']
        if cmds.namespace(exists=namespace):
            members = cmds.namespaceInfo(namespace, listNamespace=True)
            if not members:
                cmds.namespace(removeNamespace=namespace)
            else:
                self.log.warning("Namespace not deleted because it "
                                 "still has members: %s", namespace)
