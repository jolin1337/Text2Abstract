import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import ast

matrixDocuments = ast.literal_eval(open("classify_result_2.1_vary_documents.pjson").read())
documentLengthData = ast.literal_eval(open("classify_result_2.2_separate_document_lengths.pjson").read())
matrixDocuments.sort(key=lambda m: m['score'])
algorithms = ['neuralnetwork', 'randomforest', 'decissiontree']
for algorithm in algorithms:
    py.plot({
        'data': [
            go.Scatter(x=[measure['category_count']],
                    y=[measure['document_count'] / measure['category_count']],
                    marker=go.Marker(color='hsl('+str(measure['score']*360-90)+',50%'+',50%)', size=measure['score']*100, sizemode='area', sizeref=131868),
                    mode='markers', name=measure['score']) for measure in matrixDocuments if measure['doc2vec'] == 'original' and algorithm in measure['classifier']
        ],
        'layout': go.Layout(xaxis=go.XAxis(title='Category quantity'), yaxis=go.YAxis(title='Document quantity'))
    }, show_link=False, filename='plot-matrix-' + algorithm + '.html')

py.plot({
    'data': [
        go.Box(name=algorithm,y=[
            measure['score'] #* 10 * 10010 / (measure['category_count'] * measure['document_count'])
            for measure in matrixDocuments if measure['category_count'] == 25 and round(measure['document_count'] / (1000 * measure['category_count'])) * 1000 == 10000 and algorithm in measure['classifier']
        ])
        for algorithm in algorithms
    ],
    'layout': go.Layout(xaxis=go.XAxis(title='Category quantity'), yaxis=go.YAxis(title='Document quantity'))
}, show_link=False, filename='plot-variance-of-input-' + algorithm + '.html')

py.plot({
    'data': [
        go.Bar(
            name=algorithm,
            x=[str(measure['min_document_length']) + ' - ' + str(measure['max_document_length']) + ' words'
                for measure in documentLengthData if algorithm in measure['classifier']
            ],
            y=[measure['score'] 
                for measure in documentLengthData if algorithm in measure['classifier']
            ]
        )
        for algorithm in algorithms
    ],
    'layout': go.Layout(xaxis=go.XAxis(title='Algorithms'), yaxis=go.YAxis(title='Accuracy'))
}, show_link=False, filename='plot-document-length.html')
