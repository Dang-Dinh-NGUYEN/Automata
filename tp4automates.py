#!/usr/bin/env python3
"""
Read a regular expression and returns:
 * YES if word is recognized
 * NO if word is rejected"""

from typing import Set, List
from automaton import Automaton, EPSILON, State, error, warn, RegExpReader
import sys
import pdb # for debugging
from collections import defaultdict
 
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
  #verify if the word is construct by accepted letters
      for letter in word:
         if letter not in a.alphabet and letter != "%":
          return False 
      
   #verify if this automate is deterministic
      if not is_deterministic(a):
          return False   

   #create a dictionary which takes each pair of a.transition's source-symbol as key and value
      trans = defaultdict(list)
      for transition in a.transitions:
          trans[transition[0]].append(transition[1])
   #iterate each letter of the word
      currentState = str(a.initial)
      for currentLetter in word:
          if currentLetter == "%":
              currentState = currentState
          elif (trans.get(currentState) is None and currentState not in a.acceptstates):
              return False
          elif (currentLetter not in list(trans.get(currentState))):
              return False
          else:
              currentState = str(list(a.statesdict[str(currentState)].transitions[currentLetter])[0])
      if currentState in a.acceptstates:
          return True
      return False
  
##################

def determinise(a:Automaton):
  #create a dictionary which takes each pair of a.transition's source-symbol as key and value
  trans = transition_dictionary(a)
  
  #Algorithme d’élimination des transitions-\e
  while include_EPSILON(a):
      for transition in a.transitions:
          if transition[1] == EPSILON: #transition[1] == symbol (x) between q and k
              q = transition[0]
              k = transition[2]
              if trans.get(k) is not None:
                 for x in (trans.get(k)): #k is transition[2] >> list of symbol executed by k (liste de x(i))
                     for dest in list(a.statesdict[k].transitions[x]):
                          a.add_transition(q, x,str(dest))
                          
                          if k in a.acceptstates:
                              a.make_accept(q)
              a.remove_transition(q, transition[1], k)
  a.remove_unreachable()
  a.to_graphviz("1_sansepsilon")
  """
  if not is_deterministic(a):           
  #Algorithme de réduction des transitions
      new_states = [set([a.initial.name])] #cas à traiter
      det = Automaton("det") #initialise new automata deterministic
      traited_states = []
       
  #add new states,transitions and accepted states
      for new_state in new_states:
              for state in new_state:
                    if trans.get(state) is not None:
                        for symbol in list(set(trans.get(state))):
                                set_destinations = set()
                                for i in range (0,len(list(a.statesdict[state].transitions[symbol]))):
                                  set_destinations.add((str(list(a.statesdict[state].transitions[symbol])[i])))
                                if set_destinations not in new_states:
                                    new_states.append(set_destinations)    
                                if len(list(set_destinations)) > 0 :
                                    det.add_transition(str(new_state),symbol,str(set_destinations))
                                
                                    #if len(list(det.statesdict[str(new_state)].transitions[symbol])) > 1:
                                     # det.remove_transition(str(new_state), symbol,str(set_destinations))
      for new_state in new_states:  
            for state in new_state: 
                  if state in a.acceptstates:
                      det.make_accept(str(new_state))
              
      namecount = 0 # On va numéroter les nouveaux états 0, 1, 2...
      for statename in det.states : # Pour tous les états du nouvel automate
            newname = str(namecount) # transformer int -> str
            det.rename_state(statename, newname) # renommer l'état est une fonction de␣,!la bibliothèque
            namecount = namecount + 1 # incrémente le compteur de nouveaux états
      a =  det.deepcopy()
      a.remove_unreachable()
      a.to_graphviz("1_determinsed")
      """
  return a

##################

def kleene(a1:Automaton)->Automaton:
  a_kleene = a1.deepcopy()
  a_kleene.name = "kleene"
  
  for state in a_kleene.acceptstates:
      a_kleene.add_transition(state,EPSILON,a_kleene.initial.name)

  nom_nouvel_etat = nouvel_etat(a_kleene)
  a_kleene.add_transition(nom_nouvel_etat,EPSILON,a1.initial.name)
  a_kleene.initial = a_kleene.statesdict[nom_nouvel_etat]
  a_kleene.make_accept(nom_nouvel_etat)
  
  return a_kleene

##################

def nouvel_etat(a1:Automaton)->str:
   maxstate = -1
   for a in a1.states :
        try : maxstate = max(int(a),maxstate)
        except ValueError: pass # ce n'est pas un entier, on ignore
   return str(maxstate + 1)
           
##################

def concat(a1:Automaton, a2:Automaton)->Automaton:
  a1_a2 = a1.deepcopy()
  a1_a2.name = "a1_a2"
  
  nom_nouvel_etat = nouvel_etat(a1_a2)
  for s in a2.states :
      if s in a1_a2.states : # l'état de a2 existe dans la copie de a1
          a2.rename_state(s,nom_nouvel_etat) # ici on modifie a2 directement -> à␣,!éviter
          nom_nouvel_etat = str(int(nom_nouvel_etat) + 1) # incrémente le compteur
          
  for (s,a,d) in a2.transitions:
      a1_a2.add_transition(s,a,d)
  a1_a2.make_accept(a2.acceptstates)
      
  for ac in a1.acceptstates:
      a1_a2.add_transition(ac,EPSILON,a2.initial.name)
      
  a1_a2.make_accept(a1.acceptstates, accepts = False) # transforme en états␣,!non acceptants
  
  return a1_a2

##################

def union(a1:Automaton, a2:Automaton)->Automaton:
  a1_or_a2 = a1.deepcopy()
  a1_or_a2.name = "a1_or_a2"
  
  nom_nouvel_etat = nouvel_etat(a1_or_a2)
  for s in a2.states :
      if s in a1_or_a2.states :
          a2.rename_state(s,nom_nouvel_etat) # ici on modifie a3 directement -> à␣,!éviter
          nom_nouvel_etat = str(int(nom_nouvel_etat) + 1) # incrémente le compteur
          
  for (s,a,d) in a2.transitions:
    a1_or_a2.add_transition(s,a,d)
  a1_or_a2.make_accept(a2.acceptstates)
  
  a1_or_a2.add_transition(nom_nouvel_etat,EPSILON,a1.initial.name)
  a1_or_a2.add_transition(nom_nouvel_etat,EPSILON,a2.initial.name)
  a1_or_a2.initial = a1_or_a2.statesdict[nom_nouvel_etat]
  
  return a1_or_a2
  
##################
   
def regexp_to_automaton(re:str)->Automaton:
  """
  Moore's algorithm: regular expression `re` -> non-deterministic automaton
  """
  postfix = RegExpReader(regexp).to_postfix()
  stack:List[Automaton] = []
  #TODO implement!
  for symbol in postfix:
      if symbol.isalpha() or symbol.isalnum() or symbol == "%":
          a = Automaton(symbol)
          a.add_transition("0",symbol,"1")
          a.make_accept("1")
          stack.append(a)
      elif symbol in list(("+",".","*")):
           if symbol == "+":
               right = stack.pop()
               left = stack.pop()
               result = union(left,right)
               #name = "union({},{})".format(left.name,right.name)
               #result = Automaton(name)
               stack.append(result)
           elif symbol == "*":
               left = stack.pop()
               result = kleene(left)
               stack.append(result)
           else:
               right = stack.pop()
               left = stack.pop()
               result = concat(left,right)
               #name = "union({},{})".format(left.name,right.name)
               #result = Automaton(name)
               stack.append(result)
  return stack[-1]
  
##################

if __name__ == "__main__" :

  if len(sys.argv) != 3:
    usagestring = "Usage: {} <regular-expression> <word-to-recognize>"
    error(usagestring.format(sys.argv[0]))

  regexp = sys.argv[1]  
  word = sys.argv[2]

  a = regexp_to_automaton(regexp)
  a.to_graphviz("expression")
  determinise(a)
  a.to_graphviz("expression-determinised")
  if recognizes(a, word):
    print("YES")
  else:
    print("NO")

