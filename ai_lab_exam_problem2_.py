# -*- coding: utf-8 -*-
"""AI Lab Exam Problem2 .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IuBJVdux1jhtL_BLZEpmScBqWjKxs6N1

#Problem 2
# Hospital Beds Management During Covid
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import poisson
import sys

class Hospital:
    @staticmethod
    def max_beds():
        return 45
    
    @staticmethod
    def γ():
        return 0.9
    
    @staticmethod
    def alpha():
        return 1000

    @staticmethod
    def beta_1():
        return 50

    @staticmethod
    def beta_2():
        return 5000

class poisson_:
    
    def __init__(self, λ):
        self.λ = λ
        
        ε = 0.01
        
        # [α , β] is the range of n's for which the pmf value is above ε
        self.α = 0
        state = 1
        self.vals = {}
        summer = 0
        
        while(1):
            if state == 1:
                temp = poisson.pmf(self.α, self.λ) 
                if(temp <= ε):
                    self.α+=1
                else:
                    self.vals[self.α] = temp
                    summer += temp
                    self.β = self.α+1
                    state = 2
            elif state == 2:
                temp = poisson.pmf(self.β, self.λ)
                if(temp > ε):
                    self.vals[self.β] = temp
                    summer += temp
                    self.β+=1
                else:
                    break    
        
        # normalizing the pmf, values of n outside of [α, β] have pmf = 0
        
        added_val = (1-summer)/(self.β-self.α)
        for key in self.vals:
            self.vals[key] += added_val
        
            
    def f(self, n):
        try:
            Ret_value = self.vals[n]
        except(KeyError):
            Ret_value = 0
        finally:
            return Ret_value


class Beds:
    def __init__(self, requests, discharges):
        self.α = requests                             
        self.β = discharges                           
        self.poissonα = poisson_(self.α)
        self.poissonβ = poisson_(self.β)

Normal_Ward = Beds(3,3)
Covid_Ward = Beds(4,2)




#Initializing the value and policy matrices. Initial policy has zero value for all states.

value = np.zeros((Hospital.max_beds()+1, Hospital.max_beds()+1))
policy = value.copy().astype(int)




def apply_action(state, action):
    return [max(min(state[0] - action, Hospital.max_beds()),0) , max(min(state[1] + action, Hospital.max_beds()),0)]


def expected_reward(state, action):
    global value
    """
    state  : It's a pair of integers, # of beds at Normal_Ward and at Covid_Ward
    action : # of beds transferred from Normal_Ward to Covid_Ward, 
    """
    
    
    Cost = 0 #reward
    new_state = apply_action(state, action)
    
    # adding reward for moving beds from one location to another (which is negative) 
    
    Cost = Cost + Hospital.alpha() * abs(action)
    
    
    #there are four discrete random variables which determine the probability distribution of the reward and next state
    
    for Normal_Wardα in range(Normal_Ward.poissonα.α, Normal_Ward.poissonα.β):
        for Covid_Wardα in range(Covid_Ward.poissonα.α, Covid_Ward.poissonα.β):
            for Normal_Wardβ in range(Normal_Ward.poissonβ.α, Normal_Ward.poissonβ.β):
                for Covid_Wardβ in range(Covid_Ward.poissonβ.α, Covid_Ward.poissonβ.β):
                    """
                    Normal_Wardα : sample of beds requested at location Normal_Ward
                    Normal_Wardβ : sample of beds discharges at location Normal_Ward
                    Covid_Wardα : sample of beds requested at location Covid_Ward
                    Covid_Wardβ : sample of beds discharges at location Covid_Ward
                    TranProb  : probability of this event happening
                    """

                    # all four variables are independent of each other
                    TranProb = Normal_Ward.poissonα.vals[Normal_Wardα] * Covid_Ward.poissonα.vals[Covid_Wardα] * Normal_Ward.poissonβ.vals[Normal_Wardβ] * Covid_Ward.poissonβ.vals[Covid_Wardβ]
                    
                    valid_requests_Normal_Ward = min(new_state[0], Normal_Wardα)
                    valid_requests_Covid_Ward = min(new_state[1], Covid_Wardα)
                    
                    rew = (valid_requests_Normal_Ward + valid_requests_Covid_Ward)*(Hospital.alpha())
                    
                    #calculating the new state based on the values of the four random variables
                    new_s = [0,0]
                    new_s[0] = max(min(new_state[0] - valid_requests_Normal_Ward + Normal_Wardβ, Hospital.max_beds()),0)
                    new_s[1] = max(min(new_state[1] - valid_requests_Covid_Ward + Covid_Wardβ, Hospital.max_beds()),0)
                    
                    #Bellman's equation
                    Cost += TranProb * (rew + Hospital.γ() * value[new_s[0]][new_s[1]])
                    
    return Cost




def policy_evaluation():
    
    global value
    
    # here policy_evaluation has a static variable ε whose values decreases over time
    ε = policy_evaluation.ε
    
    policy_evaluation.ε /= 10 
    
    while(1):
        δ = 0
        
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                # value[i][j] denotes the value of the state [i,j]
                
                old_val = value[i][j]
                value[i][j] = expected_reward([i,j], policy[i][j])
                
                δ = max(δ, abs(value[i][j] - old_val))
                print(end = '')
                sys.stdout.flush()
        print(δ)
        sys.stdout.flush()
    
        if δ < ε:
            break




#initial value of ε
policy_evaluation.ε = 50




def policy_improvement():
    
    global policy
    
    policy_stable = True
    for i in range(value.shape[0]):
        for j in range(value.shape[1]):
            old_action = policy[i][j]
            
            max_act_val = None
            max_act = None
            
            τ12 = min(i,5)       
            τ21 = -min(j,5)      
            
            for act in range(τ21,τ12+1):
                σ = expected_reward([i,j], act)
                if max_act_val == None:
                    max_act_val = σ
                    max_act = act
                elif max_act_val < σ:
                    max_act_val = σ
                    max_act = act
                
            policy[i][j] = max_act
            
            if old_action!= policy[i][j]:
                policy_stable = False
    
    return policy_stable




def save_policy():
    save_policy.counter += 1
    ax = sns.heatmap(policy, linewidth=0.5)
    ax.invert_yaxis()
    plt.savefig('policy'+str(save_policy.counter)+'.svg')
    plt.close()
    
def save_value():
    save_value.counter += 1
    ax = sns.heatmap(value, linewidth=0.5)
    ax.invert_yaxis()
    plt.savefig('value'+ str(save_value.counter)+'.svg')
    plt.close()




save_policy.counter = 0
save_value.counter = 0




while(1):
    policy_evaluation()
    ρ = policy_improvement()
    save_value()
    save_policy()
    if ρ == True:
        break

print(policy)

import matplotlib.pylab as plt
plt.subplot(211)
CS = plt.contour(policy, levels=range(-6, 6))
plt.clabel(CS)
plt.xlim([0, 20])
plt.ylim([0, 20])
plt.axis('equal')
plt.xticks(range(21))
plt.yticks(range(21))
plt.grid('on')

plt.subplot(212)
plt.pcolor(value)
plt.colorbar()
plt.axis('equal')

plt.show()