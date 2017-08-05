import plotly.offline as py
import plotly.graph_objs as go
#import pandas as pd
import ast
from numpy import median, array as nparray

matrixDocuments = ast.literal_eval(open("classify_result_2.2_vary_documents.pjson").read())
documentLengthData = ast.literal_eval(open("classify_result_2.2_separate_document_lengths.pjson").read())
matrixDocuments.sort(key=lambda m: m['score'])
algorithms = ['neuralnetwork', 'randomforest', 'decissiontree']
for algorithm in algorithms:
    py.plot({
        'data': ([
            go.Scatter(x=[measure['category_count']],
                    y=[round(measure['document_count'] / measure['category_count'] / 1000) * 1000],
                    marker=go.Marker(color=[measure['score']], size=measure['score']*70, sizemode='area', sizeref=131868, showscale=True, cmax=1.0, cmin=0, colorscale=[[0, 'hsl(0,50%,50%)'], [0.5, 'hsl(50,70%,50%)'], [1, 'hsl(90,50%,50%)']]),
                    mode='markers', showlegend=False, name=measure['score']) for measure in matrixDocuments if measure['doc2vec'] == 'original' and algorithm in measure['classifier']
        ] + [
            go.Scatter(x=[measure['category_count']],
                    y=[round(measure['document_count'] / measure['category_count'] / 1000) * 1000],
                    marker=go.Marker(color=[measure['dev_score']], size=measure['dev_score']*70, sizemode='area', sizeref=131868, showscale=True, cmax=1.0, cmin=0, colorscale=[[0, 'hsl(0,50%,50%)'], [0.5, 'hsl(50,70%,50%)'], [1, 'hsl(90,50%,50%)']]),
                    mode='markers', showlegend=False, name=measure['dev_score']) for measure in matrixDocuments if measure['doc2vec'] == 'original' and algorithm in measure['classifier']
        ]),
        'layout': go.Layout(title=algorithm.replace('ss', 's') + ' classifier', xaxis=go.XAxis(title='Category quantity'), yaxis=go.YAxis(title='Document quantity'))
    }, show_link=False, filename='plot-matrix-' + algorithm + '.html', auto_open=False)

def varianceDocument(algorithm):
    global matrixDocuments
    return [measure['score'] for measure in matrixDocuments if measure['category_count'] == 25 and round(measure['document_count'] / (1000 * measure['category_count'])) * 1000 == 10000 and algorithm in measure['classifier']]

py.plot({
    'data': [
        go.Box(name=algorithm,y=[
            measure - median(nparray(varianceDocument(algorithm))) #* 10 * 10010 / (measure['category_count'] * measure['document_count'])
            for measure in varianceDocument(algorithm)
        ])
        for algorithm in algorithms
    ],
    'layout': go.Layout(title="Variance of document vector parameters", xaxis=go.XAxis(title='Algorithm'), yaxis=go.YAxis(title='Score'))
}, show_link=False, filename='plot-variance-of-input.html', auto_open=False)

py.plot({
    'data': [
        go.Bar(
            name=algorithm,
            x=[str(measure['min_document_length']) + ' - ' + str(measure['max_document_length']-1) + ' words'
                for measure in documentLengthData if algorithm in measure['classifier']
            ],
            y=[measure['score'] 
                for measure in documentLengthData if algorithm in measure['classifier']
            ]
        )
        for algorithm in algorithms
    ],
    'layout': go.Layout(title="Evaluation of the document lengths impact on the score", xaxis=go.XAxis(title='Algorithms'), yaxis=go.YAxis(title='Score'))
}, show_link=False, filename='plot-document-length.html', auto_open=False)


import gradings
grades = gradings.fetchGrades()

py.plot({
    'data': [
        go.Bar(
            name=str(i+1) + '-th iteration',
            x=[cl for cl, count in countTree.iteritems()],
            y=[count for cl, count in countTree.iteritems()]
        )
        for i, countTree in enumerate(grades['count-tree'])
    ],
    'layout': go.Layout(barmode='stack', title="Histogram of user grades", xaxis=go.XAxis(title='Grade', dtick=0.25), yaxis=go.YAxis(title='Sentence quantity'))
}, show_link=False, filename='plot-phrase-user-count-tree.html')
py.plot({
    'data': [
        go.Bar(
            name=str(i+1) + '-th iteration',
            x=[cl for cl, count in countTree.iteritems()],
            y=[count for cl, count in countTree.iteritems()]
        )
        for i, countTree in enumerate(grades['count-tree-control'])
    ],
    'layout': go.Layout(barmode='stack', title="Histogram of user grades", xaxis=go.XAxis(title='Grade', dtick=0.25), yaxis=go.YAxis(title='Sentence quantity'))
}, show_link=False, filename='plot-phrase-user-count-tree-control.html')
py.plot({
    'data': [
        go.Box(name='Validation grades', y=[g for g in grades['mean-validate-grades']]),
        go.Box(name='Control positive grades', y=[g for g in grades['mean-control-pos-grades']]),
        go.Box(name='Control negative grades', y=[g for g in grades['mean-control-neg-grades']]),
        go.Box(name='Document vector grades', y=[g for g in grades['doc2vec-grades']])
    ],
    'layout': go.Layout(title="Variations of the grades", xaxis=go.XAxis(title='Data-set'), yaxis=go.YAxis(title='Sentence grade'))
}, show_link=False, filename='plot-phrase-box-data-sets.html')