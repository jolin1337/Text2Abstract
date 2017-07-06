import plotly.offline as py
import plotly.graph_objs as go
#import pandas as pd
import ast
from numpy import median, array as nparray

matrixDocuments = ast.literal_eval(open("classify_result_2.3_vary_params_documents.pjson").read())
matrixDocuments.sort(key=lambda m: m['score'])
print "\n".join([str(measure['params']) for i, measure in enumerate(matrixDocuments) if measure['doc2vec'] == 'original' and 'randomforest' in measure['classifier'] and measure['category_count'] == 10 and round(measure['document_count'] / measure['category_count'] / 1000) * 1000 == 10000])
algorithms = ['neuralnetwork', 'randomforest', 'decissiontree']
for algorithm in algorithms:
    py.plot({
        'data': ([
            go.Scatter(x=[", ".join([str(val) for val in measure['params'].values()])],
                    y=[measure['score']],
                    name="Item " + str(i))
                   # marker=go.Marker(color=[measure['score']], size=measure['score']*70, sizemode='area', sizeref=131868, showscale=True, cmax=0.5, cmin=0, colorscale=[[0, 'hsl(0,50%,50%)'], [0.5, 'hsl(50,70%,50%)'], [1, 'hsl(90,50%,50%)']]),
                   # mode='markers', showlegend=False, name=measure['score'])
               for i, measure in enumerate(matrixDocuments) if measure['doc2vec'] == 'original' and algorithm in measure['classifier'] and measure['category_count'] == 10 and round(measure['document_count'] / measure['category_count'] / 1000) * 1000 == 10000
        ]),
        'layout': go.Layout(title=algorithm.replace('ss', 's') + ' classifier', xaxis=go.XAxis(title='Category quantity'), yaxis=go.YAxis(title='Document quantity'))
    }, show_link=False, filename='plot-params-' + algorithm + '.html', auto_open=False)