#!/usr/bin/env python3
"""
Read an automaton and a word, returns:
 * YES if word is recognized
 * NO if word is rejected
Determinises the automaton if it's non deterministic
"""

from typing import Set, List
from automaton import Automaton, EPSILON, State, error, warn
import sys
import pdb # for debugging
from collections import defaultdict
import copy


##################

def is_deterministic(a:Automaton)->bool:
    for transition in a.transitions:
        if len(list(a.statesdict[transition[0]].transitions[transition[1]])) > 1 or transition[1] == "%":
            return False
    return True  
  
##################

def include_EPSILON(a:Automaton):
    for transition in a.transitions:
        if transition[1] == "%":
            return True
    return False  

##################

#create a dictionary which takes each pair of a.transition's source-symbol as key and value
def transition_dictionary(a:Automaton):
    transition_dictionary = defaultdict(list)
    for transition in a.transitions:
        if transition[1] is not None:
            transition_dictionary[transition[0]].append(transition[1])
    return transition_dictionary

##################

def recognizes(a:Automaton, word:str)->bool:
   #verify if the word is constructed by accepted letters
      for letter in word:
         if letter not in a.alphabet and letter != "%":
          return False 
      
   #verify if this automate is deterministic
      if is_deterministic(a) == False:
          a = determinise(a)

   #iterate each letter of the word
      currentState = "0"
      for currentLetter in word:
              if currentLetter == "%":
                  currentState = currentState
              elif (transition_dictionary(a).get(currentState) is None and currentState not in a.acceptstates):
                      return False
              elif (currentLetter not in list(transition_dictionary(a).get(currentState))):
                  return False
              else:
                  currentState = str(list(a.statesdict[currentState].transitions[currentLetter])[0])
      if currentState in a.acceptstates:
              return True
      return False
  
##################

def determinise(a:Automaton):
  #create a dictionary which takes each pair of a.transition's source-symbol as key and value
  trans = transition_dictionary(a)
  a.to_graphviz("1_initialgraph")
  #Algorithme d’élimination des transitions-\e
  while include_EPSILON(a):
      for transition in  a.transitions:
          if transition[1] == EPSILON: #transition[1] == symbol (x) between q and k
              q = transition[0]
              k = transition[2]
              if trans.get(k) is not None:
                 for x in (trans.get(k)): #k is transition[2] >> list of symbol executed by k (liste de x(i))
                     for dest in list(a.statesdict[k].transitions[x]):
                          a.add_transition(q, x, str(dest))
                          
                          if k in a.acceptstates:
                              a.make_accept(q)
                              #a.remove_transition(q, transition[1], k)
                              a.remove_unreachable()
              a.remove_transition(q, transition[1], k)
  a.to_graphviz("1_sansepsilon")
  
  if not is_deterministic(a):           
  #Algorithme de réduction des transitions
    new_states = [set([a.initial.name])] #initialise Qd >> store new Automata's states
    det = Automaton("det") #initialise new automata deterministic
      
  #add new states in to list
  """
    for transition in a.transitions:
        if len(list(a.statesdict[transition[0]].transitions[transition[1]])) > 1: #in case that src-symbol leads to different destinations
           set_states = set()
           for d in (list(a.statesdict[transition[0]].transitions[transition[1]])):
               set_states.add(d.name)
           if set_states not in new_states:
               new_states.append(set_states)
        else:
            if set(transition[2]) not in new_states:
                new_states.append(set(transition[2]))
  """             
  #add new transitions and new accept states
     for new_state in new_states:
            print("new state",new_state)
            set_destinations = set()
            for state in new_state:
                if trans.get(state) is not None:
                    for symbol in list(set(trans.get(state))):
                            set_destinations = set()
                            for i in range (0,len(list(a.statesdict[state].transitions[symbol]))):
                              set_destinations.add((str(list(a.statesdict[state].transitions[symbol])[i])))
                            det.add_transition(str(new_state), symbol,str(set_destinations))
                print(str(set_destinations))
                if state in a.acceptstates:
                    det.make_accept(str(new_state))
  
                
    namecount = 0 # On va numéroter les nouveaux états 0, 1, 2...
    for statename in det.states : # Pour tous les états du nouvel automate
        newname = str(namecount) # transformer int -> str
        det.rename_state(statename, newname) # renommer l'état est une fonction de␣,!la bibliothèque
        namecount = namecount + 1 # incrémente le compteur de nouveaux états
    a =  copy.deepcopy(det)
    a.remove_unreachable()
    a.to_graphviz("1_determinsed2b")
    return a
    """
##################

if __name__ == "__main__" :
  if len(sys.argv) != 3:
    usagestring = "Usage: {} <automaton-file.af> <word-to-recognize>"
    error(usagestring.format(sys.argv[0]))

  automatonfile = sys.argv[1]  
  word = sys.argv[2]

  a = Automaton("dummy")
  a.from_txtfile(automatonfile)
  if not is_deterministic(a) :
    determinise(a)
  if recognizes(a, word):
    print("YES")
  else:
    print("NO")
##################
