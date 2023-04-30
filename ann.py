# -*- coding: utf-8 -*-
"""ANN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1G0kAkClJ26RHcQzw_lFTuJ94kjcvNCgp
"""

# Casey Detwiler
# CMPSC 445 Project
# Artifical Neural Network program

import random
import math

def sig(x):
  if x < -709: # will cause an overflow if x is allowed to go below -709
    x = -709

  return 1 / (1 + math.e ** (-x))

def sigDeriv(x):
  sigx = sig(x)
  return sigx * (1 - sigx)

def inverseSig(x):
  return -math.log(1 / x - 1)

# converts a given price to a pair of expected output nodes
# first node is the exponent, second is the coefficient
def convertToOutputNodes(price):
  exponent = math.floor(math.log(price, 10)) # [2, 4]
  coefficient = price / (10 ** exponent) # [1, 10)
  return [sig(exponent - 2) , sig((coefficient - 4.5) / 4.5)]

# converts an output by the network back into a price
def convertToPrice(nodes):
  exponent = inverseSig(nodes[0]) + 2
  coefficient = inverseSig(nodes[1]) * 4.5 + 4.5
  return coefficient * (10 ** exponent)

class Node():
  def __init__(self, numNodes, initialWeights = []): # numNodes is the number of nodes in the next layer
    if initialWeights != []:
      self.weights = initialWeights
      return

    self.weights = []

    if numNodes == 0:
      return # if it's the output layer, don't add any weights

    for i in range(numNodes):
      self.weights.append((random.random() * 2) - 1) # initial weights are real numbers between -1 and 1

class ANN():
  def __init__(self, nodesPerLayer, initValues = []): # nodesPerLayer is an array of how many nodes should be in each respective layer
    self.layers = []

    if initValues != []:
      self.numLayers = len(initValues)
      for layerWeights in initValues:
        layer = []
        for nodeWeights in layerWeights:
          layer.append(Node(0, nodeWeights))
        self.layers.append(layer)

      layer = []
      for i in range(len(initValues[-1][0]) + 1): # output layer
        layer.append(Node(0))
      self.layers.append(layer)

      self.numLayers += 1
      return

    self.numLayers = len(nodesPerLayer)
    nodesPerLayer += [0] # 0 to signify we're at the output layer
    for i in range(self.numLayers): # for each layer
      layer = []
      for j in range(nodesPerLayer[i] + 1):
        layer.append(Node(nodesPerLayer[i + 1]))

      self.layers.append(layer)

  def getWeights(self):
    w = []
    for layerIndex in range(self.numLayers - 1):
      layerWeights = []
      for node in self.layers[layerIndex]:
        nodeWeights = []
        for weight in node.weights:
          nodeWeights.append(weight)
        layerWeights.append(nodeWeights)
      w.append(layerWeights)
    return w

  def printLayers(self):
    print("Number of layers in each node, including the bias nodes:")
    for i in range(len(self.layers)):
      if i == 0:
        print("Input layer:", len(self.layers[i]), "nodes")
      elif i == len(self.layers) - 1:
        print("Output Layer:", len(self.layers[i]) - 1, "nodes")
      else:
        print("Hidden Layer " + str(i) + ":", len(self.layers[i]), "nodes")

  def __str__(self):
    output = ""
    for i in range(len(self.layers) - 1):
      layer = self.layers[i]
      output += "Layer " + str(i) + ":\n"

      for j in range(len(layer)):
        node = layer[j]

        if j == len(layer) - 1:
          output += "Bias node:\n"
        else:
          output += "Node " + str(j) + ":\n"

        for k in range(len(node.weights)):
          output += "Weight to node " + str(k) + " in next layer: " + str(node.weights[k]) + "\n"

    return output;

  # returns the output of a given sample when processed by the network, along with intermediate values if asked
  def process(self, input, returnAllValues = False):
    if len(input) != len(self.layers[0]) - 1:
      raise(Exception) # make sure it is being called with the correct number of inputs

    currentValues = input.copy() + [1]; # bias node is at the END
    intermedValues = [currentValues.copy()]

    for currentLayerIndex in range(self.numLayers - 1):
      numNextLayerNodes = len(self.layers[currentLayerIndex + 1]) - 1  # number of nodes in next layer (excluding bias)
      
      nextLayerValues = [0] * numNextLayerNodes # this is where the intermediate values will be stored
      
      #print("Layer " + str(currentLayerIndex) + ": " + str(currentValues))
      for j in range(numNextLayerNodes): # for each node in the next layer except the bias
        for k in range(len(currentValues)): # for all nodes in the current layer, including bias
          nextLayerValues[j] += self.layers[currentLayerIndex][k].weights[j] * currentValues[k]

      if returnAllValues:
        intermedValues.append(nextLayerValues.copy() + [1])

      for i in range(len(nextLayerValues)):
        nextLayerValues[i] = sig(nextLayerValues[i])

      currentValues = nextLayerValues.copy() + [1]

    if returnAllValues:
      return intermedValues, currentValues[:-1]

    return currentValues[:-1] # return everything except the bias node

  def evaluate(self, data, outputFrequency = 0):
    numSamples = len(data)
    totalError = 0
    for j in range(len(data)):
      instance = data[j]
      predicted = ANN.process(self, instance[:-1])

      if outputFrequency and j % outputFrequency == 0:
        print("Expected output:", instance[-1], "=", convertToPrice(instance[-1]))
        print("Predicted output:", predicted, "=", convertToPrice(predicted), "\n")

      for i in range(len(predicted)):
        totalError += (instance[-1][i] - predicted[i]) ** 2

    return totalError / numSamples

  def train(self, fullData, learningRate = 0.01, miniEpocheSize = 100, miniReportFreq = 20, epoches = 0, reportFreq = 1):

    numSamples = len(fullData)

    for e in range(epoches):
      for miniEpocheIndex in range(numSamples // miniEpocheSize):
        data = fullData[(miniEpocheSize * miniEpocheIndex):(miniEpocheSize * (1 + miniEpocheIndex))]
        totalCost = 0

        deltaWeights = [] # where the changes to the weights will be stored
        for layer in self.layers:
          deltaLayer = []
          for node in layer:
            deltaLayer.append([0] * len(node.weights))
          deltaWeights.append(deltaLayer)

        for instance in data:
          nodeValues, predictedOutput = ANN.process(self, instance[:-1], True)
          expectedOutput = instance[-1]

          cost = 0
          dCdaNexts = [] # the derivatives of the cost with respect to the activation of each node in the next layer
          for n in range(len(expectedOutput)):
            cost += (expectedOutput[n] - predictedOutput[n]) ** 2
            dCdaNexts.append(predictedOutput[n] - expectedOutput[n]) # might need to multiply this by 2 before appending
          totalCost += cost

          for currentLayerIndex in range(self.numLayers - 2, -1, -1): # for every layer, starting from the 2nd to last one and moving backwards
            dadzs = [] # the derivatives of the activation function w/ respect to the next layer's nodes' values
            for nNodeIndex in range(len(self.layers[currentLayerIndex + 1]) - 1): # for each node in the next layer except the bias
              dadzs.append(sigDeriv(nodeValues[currentLayerIndex + 1][nNodeIndex]))

            dCdals = [] # the derivatives of the cost with respect to the activation of the current layers' nodes; needed for next backprop iteration
            dzdws = [] # the derivatives of the next layer's nodes' values w/ respect to the current layer's nodes' weights
            for nodeIndex in range(len(self.layers[currentLayerIndex]) - 1): # for each node in the current layer except the bias

              if currentLayerIndex != 0: # take the sigmoids for all nodes except the input layer
                dzdws.append(sig(nodeValues[currentLayerIndex][nodeIndex]))
              else:
                dzdws.append(nodeValues[currentLayerIndex][nodeIndex])

              dCdal = 0
              for nNodeIndex in range(len(self.layers[currentLayerIndex + 1]) - 1): # for each node in the next layer except the bias
                dCdal += self.layers[currentLayerIndex][nodeIndex].weights[nNodeIndex] * dadzs[nNodeIndex] * dCdaNexts[nNodeIndex]
                #print(self.layers[currentLayerIndex][nodeIndex].weights[nNodeIndex], "\n", dadzs[nodeIndex], "\n", dCdaNexts[nNodeIndex], "\n", dCdal, "\n") # debug code
              dCdals.append(dCdal)

            dzdws.append(1) # bias node

            #print("dCdaNexts:", dCdaNexts, "\ndadzs:", dadzs, "\ndzdws:", dzdws, "\ndCdals:", dCdals, "\n") # debug code
            for cNodeIndex in range(len(deltaWeights[currentLayerIndex])): # for each node in the current layer, including bias
              for nNodeIndex in range(len(deltaWeights[currentLayerIndex + 1]) - 1): # for each node in the next layer, excluding bias
                deltaWeights[currentLayerIndex][cNodeIndex][nNodeIndex] += dCdaNexts[nNodeIndex] * dadzs[nNodeIndex] * dzdws[cNodeIndex]

            dCdaNexts = dCdals.copy()

        #print("deltaWeights:", deltaWeights)
        # now that we've finished an epoche, we need to update the weights with deltaWeights
        for i in range(self.numLayers - 1):
          for j in range(len(self.layers[i])):
            for k in range(len(self.layers[i][j].weights)):
              self.layers[i][j].weights[k] -= learningRate * deltaWeights[i][j][k]

        if miniReportFreq and not (miniEpocheIndex % miniReportFreq):
          print("Average cost on #" + str(miniEpocheIndex), "mini epoche:", (totalCost / numSamples))

      if reportFreq and not (e % reportFreq):
        print("Average cost after", e, "epoches:", ANN.evaluate(self, fullData))
        print("Weights:")
        print(self.getWeights())
    print("Average cost after training:", ANN.evaluate(self, fullData))

# Data preprocessing in this cell
import math
from pandas.core.internals.blocks import F
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import random

df = pd.read_csv("encoded_df.csv")
df.head()

# converts a given price to a pair of expected output nodes
# first node is the exponent, second is the coefficient
def convertToOutputNodes(price):
  exponent = math.floor(math.log(price, 10)) # [2, 4]
  coefficient = price / (10 ** exponent) # [1, 10)
  return [sig(exponent - 2) , sig((coefficient - 4.5) / 4.5)]

# converts an output by the network back into a price
def convertToPrice(nodes):
  exponent = inverseSig(nodes[0]) + 2
  coefficient = inverseSig(nodes[1]) * 4.5 + 4.5
  return coefficient * (10 ** exponent)

# scale an attribute to range between 0 and 1
def min_max_scaling(series):
  return (series - series.min()) / (series.max() - series.min())

def encodePrices(series):
  result = []
  for i in series:
    result.append(convertToOutputNodes(i))
  return result

# remove all entries where the price exceeds $10000
df = df.loc[df["total_sales_price"] <= 10000]

# store the original ranges to scale new inputs
caratRange = [df["carat_weight"].min(), df["carat_weight"].max()]
dpRange = [df["depth_percent"].min(), df["depth_percent"].max()]
tpRange = [df["table_percent"].min(), df["table_percent"].max()]

# scale all non-label features to be between 0 and 1
df["carat_weight"] = min_max_scaling(df["carat_weight"])
df["depth_percent"] = min_max_scaling(df["depth_percent"])
df["table_percent"] = min_max_scaling(df["table_percent"])

# encode the prices to serve as expected output nodes for training
df["encoded_price"] = encodePrices(df["total_sales_price"])

# remove the original price column; it is no longer needed
df.drop(labels = ["total_sales_price"], axis = 1, inplace = True)

# replace 0s with 0.01 since there will be a lot of 0s with one-hot encoding
for attr in df:
  df[attr] = df[attr].replace(0, 0.01)

data = df.to_numpy() # convert data to an array
numAttributes = len(df.columns)
random.shuffle(data) # shuffle the data so that it's not in an increasing order

numInstances = len(data)
trainingData = data[:(numInstances) // 5 * 4] # 80% of the data is for training
testingData = data[(numInstances) // 5 * 4:] # 20% of the data is for testing

NN = ANN([numAttributes - 1, 5, 5, 2])

NN.train(trainingData, learningRate = 0.01, miniEpocheSize = 500, epoches = 5000, miniReportFreq = 0, reportFreq = 25)

print(NN.getWeights())

pass

# Performance evaluation cell

NN.evaluate(testingData, 1000)

# sources

# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_numpy.html
# https://datagy.io/pandas-normalize-column/
# https://www.shanelynn.ie/pandas-drop-delete-dataframe-rows-columns/
# https://builtin.com/data-science/pandas-add-column