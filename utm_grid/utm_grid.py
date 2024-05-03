import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

class UTM:
  def __init__(self, zone):
    self._zone = zone

def main():
  zone = ['47N','47P','47Q','48P','48Q' ]
  df = pd.DataFrame()
  for z in zone:
    df = df.append({'name':z}, ignore_index=True)
  print(df)
  g = nx.Graph()

  g.add_node('UTM', label='UTM', level=1)
  for z in zone:
    g.add_node(z, label=z, level=2)
    g.add_edge('UTM', z, object={})

  g.add_node('NCDC', label='NCDC', level=1)
  nx.draw(g, with_labels=True)
  plt.savefig("utm_docs.png")

if __name__ == '__main__':
  main()
