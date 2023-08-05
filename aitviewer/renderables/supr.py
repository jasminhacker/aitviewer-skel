"""
Copyright (C) 2022  ETH Zurich, Manuel Kaufmann, Velko Vechev, Dario Mylonopoulos

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import numpy as np

from aitviewer.configuration import CONFIG as C
from aitviewer.models.supr import SUPRLayer
from aitviewer.renderables.smpl import SMPLSequence
from aitviewer.utils import to_numpy as c2c


class SUPRSequence(SMPLSequence):
    """
    Represents a temporal sequence of SMPL poses using the SUPR model.
    """

    def __init__(
        self,
        poses_body,
        smpl_layer,
        poses_root,
        betas=None,
        trans=None,
        device=None,
        include_root=True,
        normalize_root=False,
        is_rigged=True,
        show_joint_angles=False,
        z_up=False,
        post_fk_func=None,
        **kwargs,
    ):
        super(SUPRSequence, self).__init__(
            poses_body,
            smpl_layer,
            poses_root,
            betas,
            trans,
            device=device,
            include_root=include_root,
            normalize_root=normalize_root,
            is_rigged=is_rigged,
            show_joint_angles=show_joint_angles,
            z_up=z_up,
            post_fk_func=post_fk_func,
            **kwargs,
        )

    def fk(self, current_frame_only=False):
        """Get joints and/or vertices from the poses."""
        if current_frame_only:
            # Use current frame data.
            if self._edit_mode:
                poses_root = self._edit_pose[:3][None, :]
                poses_body = self._edit_pose[3:][None, :]
            else:
                poses_body = self.poses_body[self.current_frame_id][None, :]
                poses_root = self.poses_root[self.current_frame_id][None, :]

            trans = self.trans[self.current_frame_id][None, :]

            if self.betas.shape[0] == self.n_frames:
                betas = self.betas[self.current_frame_id][None, :]
            else:
                betas = self.betas
        else:
            # Use the whole sequence.
            if self._edit_mode:
                poses_root = self.poses_root.clone()
                poses_body = self.poses_body.clone()
                poses_root[self.current_frame_id] = self._edit_pose[:3]
                poses_body[self.current_frame_id] = self._edit_pose[3:]
            else:
                poses_body = self.poses_body
                poses_root = self.poses_root
            trans = self.trans
            betas = self.betas

        verts, joints = self.smpl_layer(
            poses_root=poses_root,
            poses_body=poses_body,
            betas=betas,
            trans=trans,
            normalize_root=self._normalize_root,
        )

        skeleton = self.smpl_layer.skeletons()["body"].T
        faces = self.smpl_layer.faces
        joints = joints[:, : skeleton.shape[0]]

        if current_frame_only:
            return c2c(verts)[0], c2c(joints)[0], c2c(faces), c2c(skeleton)
        else:
            return c2c(verts), c2c(joints), c2c(faces), c2c(skeleton)

    @classmethod
    def from_amass(
        cls,
        npz_data_path,
        start_frame=None,
        end_frame=None,
        sub_frames=None,
        log=True,
        fps_out=None,
        load_betas=False,
        z_up=True,
        **kwargs,
    ):
        raise ValueError("SUPR does not support loading from 3DPW.")

    @classmethod
    def from_3dpw(cls, **kwargs):
        raise ValueError("SUPR does not support loading from 3DPW.")

    @classmethod
    def t_pose(cls, model=None, betas=None, frames=1, **kwargs):
        """Creates a SMPL sequence whose single frame is a SMPL mesh in T-Pose."""

        if model is None:
            model = SUPRLayer(device=C.device)

        poses_body = np.zeros([frames, model.n_joints_body * 3])
        poses_root = np.zeros([frames, 3])
        return cls(
            poses_body=poses_body,
            smpl_layer=model,
            poses_root=poses_root,
            betas=betas,
            **kwargs,
        )
