# -*- coding: utf-8 -*-
"""MIProjectDynamicEnvironment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xoRS2UL_umeNaTSvjHQjJRXnoKj3H9uL
"""

import gym
from gym import spaces
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

class AdvancedRobotEnv(gym.Env):
    """A more complex environment for robotic navigation with static and dynamic obstacles."""

    def __init__(self):
        super(AdvancedRobotEnv, self).__init__()
        self.grid_size = 20  # Define the grid size
        self.action_space = spaces.Discrete(4)  # Define the action space (up, down, left, right)
        self.num_static_obstacles = 3  # Define the number of static obstacles
        self.num_dynamic_obstacles = 2  # Define the number of dynamic obstacles
        self.observation_space = spaces.Box(low=0, high=self.grid_size,
                                            shape=(2 + 2 * self.num_static_obstacles + 2 * self.num_dynamic_obstacles,), dtype=np.int32)

        self.state = None  # Initialize the state
        self.goal_position = np.array([self.grid_size - 1, self.grid_size - 1])  # Set the goal position
        self.ani = None  # To keep the reference to the animation

        # Generate static and dynamic obstacles
        self.static_obstacles = [self._random_position() for _ in range(self.num_static_obstacles)]
        self.dynamic_obstacles = [self._random_position() for _ in range(self.num_dynamic_obstacles)]
        self.reset()

    def reset(self):
        """Reset the environment state."""
        self.state = np.array([0, 0])  # Starting position of the robot
        return self.state

    def step(self, action):
        """Update the environment state based on an action."""
        # Move the robot
        self.state[:2] = self._move_robot(self.state[:2], action)

        # Update dynamic obstacles
        for i in range(self.num_dynamic_obstacles):
            self.dynamic_obstacles[i] = self._move_obstacle(self.dynamic_obstacles[i])

        # Check for collisions with static and dynamic obstacles
        collision_static = any(np.array_equal(self.state[:2], obstacle) for obstacle in self.static_obstacles)
        collision_dynamic = any(np.array_equal(self.state[:2], obstacle) for obstacle in self.dynamic_obstacles)
        collision = collision_static or collision_dynamic

        # Determine if the goal has been reached
        done = np.array_equal(self.state[:2], self.goal_position)
        reward = self._calculate_reward(done, collision)

        return self.state, reward, done, {}

    def _random_position(self):
        """Generate a random position within the grid."""
        return np.array([random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)])

    def _move_robot(self, position, action):
        """Move the robot based on the action."""
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        new_position = position + moves[action]
        new_position = np.clip(new_position, 0, self.grid_size - 1)
        return new_position.astype(int)

    def _move_obstacle(self, position):
        """Randomly move a dynamic obstacle to a new position."""
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]  # Add a stationary move
        move = random.choice(moves)
        new_position = position + move
        new_position = np.clip(new_position, 0, self.grid_size - 1)
        return new_position.astype(int)

    def _check_collision(self):
        """Check if the robot has collided with any obstacle."""
        for obstacle in self.static_obstacles + self.dynamic_obstacles:
            if np.array_equal(self.state[:2], obstacle):
                return True
        return False

    def _calculate_reward(self, done, collision):
        """Calculate the reward based on the current state."""
        if done:
            return 10  # High reward for reaching the goal
        elif collision:
            return -10  # High penalty for collision
        else:
            return -1  # Small penalty for each step to encourage efficiency

    def animate_step(self, i, fig, ax):
        """Animation step function."""
        ax.clear()
        ax.set_xlim(0, self.grid_size)
        ax.set_ylim(0, self.grid_size)
        plt.grid()

        # Update robot and obstacles positions
        action = self.action_space.sample()  # Replace with your algorithm's action
        self.step(action)

        # Draw the robot
        robot = patches.Circle((self.state[1] + 0.5, self.grid_size - self.state[0] - 0.5), 0.4, color='blue')
        ax.add_patch(robot)

        # Draw static obstacles
        for obstacle in self.static_obstacles:
            static = patches.Rectangle((obstacle[1] + 0.1, self.grid_size - obstacle[0] - 0.9), 0.8, 0.8, color='grey')
            ax.add_patch(static)

        # Draw dynamic obstacles
        for obstacle in self.dynamic_obstacles:
            dynamic = patches.Rectangle((obstacle[1] + 0.1, self.grid_size - obstacle[0] - 0.9), 0.8, 0.8, color='orange')
            ax.add_patch(dynamic)

        # Draw the goal
        goal = patches.Rectangle((self.goal_position[1] + 0.1, self.grid_size - self.goal_position[0] - 0.9), 0.8, 0.8, color='green')
        ax.add_patch(goal)

    def start_animation(self, steps=50):
        """Start the environment animation."""
        fig, ax = plt.subplots()
        self.ani = FuncAnimation(fig, self.animate_step, frames=steps, fargs=(fig, ax), interval=200)
        plt.show()

# Testing the environment with animation
env = AdvancedRobotEnv()
env.reset()
env.start_animation(steps=50)  # Start the animation

