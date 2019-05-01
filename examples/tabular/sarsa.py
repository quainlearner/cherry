#!/usr/bin/env python3

import gym

import torch.nn as nn
import torch.optim as optim

import cherry as ch
import cherry.envs as envs
from cherry.models.tabular import ActionValueFunction
from cherry.distributions import EpsilonGreedy


class Agent(nn.Module):

    def __init__(self, env):
        super(Agent, self).__init__()
        self.env = env
        self.qf = ActionValueFunction(env.state_size,
                                      env.action_size)
        self.e_greedy = EpsilonGreedy(0.1)

    def forward(self, x):
        x = ch.utils.onehot(x, self.env.state_size)
        q_values = self.qf(x)
        action = self.e_greedy(q_values)
        info = {
            'q_action': q_values[:, action],
        }
        return action, info


def main(env='CliffWalking-v0'):
    env = gym.make(env)
    env = envs.Logger(env, interval=1000)
    env = envs.Torch(env)
    env = envs.Runner(env)
    agent = Agent(env)
    discount = 1.00
    optimizer = optim.SGD(agent.parameters(), lr=0.5, momentum=0.0)
    for t in range(1, 10000):
        transition = env.run(agent, steps=1)[0]

        curr_q = transition.q_action
        next_action, next_info = agent(transition.next_state)
        next_q = next_info['q_action'].detach()
        td_error = temporal_difference(discount,
                                       transition.reward,
                                       transition.done,
                                       curr_q,
                                       next_q)

        optimizer.zero_grad()
        loss = td_error.pow(2).mul(0.5)
        loss.backward()
        optimizer.step()


if __name__ == '__main__':
    main()
