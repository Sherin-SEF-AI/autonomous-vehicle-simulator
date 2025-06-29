"""
Physics engine integration using PyBullet for real-time vehicle simulation.
"""

import pybullet as p
import pybullet_data
import numpy as np

class PhysicsEngine:
    def __init__(self, gui=False):
        self.client = p.connect(p.GUI if gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.client)
        p.setGravity(0, -9.81, 0, physicsClientId=self.client)
        self.time_step = 1.0 / 60.0
        p.setTimeStep(self.time_step, physicsClientId=self.client)
        self.vehicle_id = None
        self.vehicle_state = {
            'position': [0, 0, 0],
            'orientation': [0, 0, 0, 1],
            'velocity': [0, 0, 0],
            'angular_velocity': [0, 0, 0]
        }
        self._setup_world()

    def _setup_world(self):
        # Load ground plane
        self.plane_id = p.loadURDF("plane.urdf", physicsClientId=self.client)
        # Load a simple vehicle (box for now)
        self.vehicle_id = p.loadURDF(
            "r2d2.urdf", [0, 0.1, 0], useFixedBase=False, physicsClientId=self.client
        )

    def step(self, throttle=0.0, brake=0.0, steering=0.0):
        # Simple forward force for demonstration
        force = 1000 * throttle - 1000 * brake
        p.applyExternalForce(
            self.vehicle_id, -1, [force, 0, 0], [0, 0, 0], p.LINK_FRAME, physicsClientId=self.client
        )
        # Simple steering: apply torque
        p.applyExternalTorque(
            self.vehicle_id, -1, [0, steering * 100, 0], p.LINK_FRAME, physicsClientId=self.client
        )
        p.stepSimulation(physicsClientId=self.client)
        self._update_vehicle_state()

    def _update_vehicle_state(self):
        pos, orn = p.getBasePositionAndOrientation(self.vehicle_id, physicsClientId=self.client)
        lin_vel, ang_vel = p.getBaseVelocity(self.vehicle_id, physicsClientId=self.client)
        self.vehicle_state = {
            'position': pos,
            'orientation': orn,
            'velocity': lin_vel,
            'angular_velocity': ang_vel
        }

    def get_vehicle_state(self):
        return self.vehicle_state.copy()

    def reset(self):
        p.resetBasePositionAndOrientation(self.vehicle_id, [0, 0.1, 0], [0, 0, 0, 1], physicsClientId=self.client)
        p.resetBaseVelocity(self.vehicle_id, [0, 0, 0], [0, 0, 0], physicsClientId=self.client)
        self._update_vehicle_state()

    def disconnect(self):
        p.disconnect(physicsClientId=self.client) 