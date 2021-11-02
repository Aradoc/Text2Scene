"""
    Many small add-ons in this program come from various sources online.
    like: -https://stackoverflow.com/questions/23240969/python-count-repeated-elements-in-the-list
          -https://docs.python.org/3/library/xml.etree.elementtree.html
          -https://stackoverflow.com/questions/5316206/converting-dot-to-png-in-python/5316307
"""
# import graphviz
import graphviz
import matplotlib.pyplot as plt
import tkinter as tk
import prettytable
# import graphviz
# import tempfile
# import image

# import pydot
import spacy

from xml.etree import cElementTree as ET
# from subprocess import check_call
from collections import Counter
from tkinter import filedialog
# from graphviz import dot


# from PIL import Image
# from graphviz import render


# ##### 2.3 ##### #
def PoS():
    nlp = spacy.load('en_core_web_sm')
    nlp.max_length = 5000000
    text = root.find('TEXT').text
    # print(text)
    doc = nlp(text)

    pos_lst = []
    for token in doc:
        pos_lst.append(token.pos_)
    PoS_dict = {i: pos_lst.count(i) for i in pos_lst}
    return PoS_dict


def Qs():
    links = []
    for qslink in root.iter('QSLINK'):
        links.append(qslink.attrib.get('relType'))
    QsLink = {i: links.count(i) for i in links}
    return QsLink


def ISO():
    temp = ['SPATIAL_ENTITY', 'PLACE', 'MOTION', 'LOCATION', 'SIGNAL', 'QSLINK', 'OLINK']
    ISOs = []
    for iso_ in (elem.tag for elem in root.iter()):
        if iso_ in temp:
            ISOs.append(iso_)
    ISOd = {i: ISOs.count(i) for i in ISOs}
    return ISOd


def sentence_length():
    text = root.find('TEXT').text
    rows = text.split('\n')
    rows = list(filter(None, rows))
    tmp = []
    for i in range(len(rows)):
        if rows[i].__contains__('. '):
            tmp.append(rows[i].split('. '))
        else:
            tmp.append(rows[i])
    sentences = []

    for i in range(len(tmp)):
        if isinstance(tmp[i], list):
            for _ in tmp[i]:
                sentences.append(_)
        else:
            sentences.append(tmp[i])
    filter(None, sentences)

    WordsPerSent = []
    for i in range(len(sentences)):
        WordsPerSent.append(sentences[i].split())

    len_sentences = []
    for i in range(len(WordsPerSent)):
        counter = 0
        for j in range(len(WordsPerSent[i])):
            counter += 1
        len_sentences.append(counter)

    len_freq = {i: len_sentences.count(i) for i in len_sentences}
    plt.bar(list(len_freq.keys()), len_freq.values(), color="orange")
    plt.xlabel("Nbr of Words")
    plt.ylabel("Frequency")
    plt.show()


def prepositions():
    sp_signals = []
    for sp_signal in root.iter('SPATIAL_SIGNAL'):
        sp_signals.append([sp_signal.attrib['id'], sp_signal.attrib['text']])

    qs_links = []
    for qs_link in root.iter('QSLINK'):
        qs_links.append([qs_link.attrib['trigger'], qs_link.attrib['id']])

    o_links = []
    for o_link in root.iter('OLINK'):
        o_links.append([o_link.attrib['trigger'], o_link.attrib['id']])

    prep_qs_mark = []
    prep_ol_mark = []
    prep_comp = []
    for i in range(len(sp_signals)):
        for j in range(len(qs_links)):
            if sp_signals[i][0] == qs_links[j][0]:
                prep_qs_mark.append(sp_signals[i][1])
        for k in range(len(o_links)):
            if sp_signals[i][0] == o_links[k][0]:
                prep_ol_mark.append(sp_signals[i][1])
    for i in range(len(prep_qs_mark)):
        prep_comp.append(prep_qs_mark[i])
    for i in range(len(prep_ol_mark)):
        prep_comp.append(prep_ol_mark[i])
    prep_qs = {i: prep_qs_mark.count(i) for i in prep_qs_mark}
    prep_ol = {i: prep_ol_mark.count(i) for i in prep_ol_mark}
    prep = {i: prep_comp.count(i) for i in prep_comp}
    return prep_qs, prep_ol, prep


def motion():
    verbs = []
    for verb in root.iter('MOTION'):
        verbs.append(verb.attrib['text'])
    verb_dict = {i: verbs.count(i) for i in verbs}
    # return sorted(verb_dict, key=verb_dict.get, reverse=True)[:5]
    return dict(Counter(verb_dict).most_common(5))


# ##### 2.4 ##### #
def visualization(location):
    # #### Vertices #### #
    # (PLACE, LOCATION, SPATIAL_ENTITY, NONMOTION_EVENT, PATH)
    IDs = []
    for path in root.iter('PATH'):
        IDs.append((path.attrib['id'], path.attrib['text']))
    for place in root.iter('PLACE'):
        IDs.append((place.attrib['id'], place.attrib['text']))
    for location in root.iter('LOCATION'):
        IDs.append((location.attrib['id'], location.attrib['text']))
    for sp_entity in root.iter('SPATIAL_ENTITY'):
        IDs.append((sp_entity.attrib['id'], sp_entity.attrib['text']))
    for nmotion_event in root.iter('NONMOTION_EVENT'):
        IDs.append((nmotion_event.attrib['id'], nmotion_event.attrib['text']))

    metalink = []
    for meta in root.iter('METALINK'):
        metalink.append((meta.attrib['fromID'], meta.attrib['toID']))

    # #### EDGES #### #
    edge = []

    for ol in root.iter('OLINK'):
        edge.append((ol.attrib['fromID'], ol.attrib['toID'], ol.attrib['relType']))
    for qs in root.iter('QSLINK'):
        edge.append((qs.attrib['fromID'], qs.attrib['toID'], qs.attrib['relType']))

    node = IDs
    for (x, y) in metalink:
        cnt = 0
        for (i, j) in node:
            if x == i:
                node[cnt] = (y, j)
                cnt += 1
            else:
                cnt += 1
        cnt = 0
        for (from_, to_, type_) in edge:
            if x == from_:
                edge[cnt] = (y, to_, type_)
                cnt += 1
            elif x == to_:
                edge[cnt] = (from_, y, type_)
                cnt += 1
            else:
                cnt += 1

    f = open(location + "\\graph.dot", "w", encoding="utf8")
    f.write("DIGRAPH Text2Scene" + "\n" + "{" + "\n")

    for (i, j) in node:
        # node [label="xxx"];
        f.write(str(i) + ' [label="' + str(j) + '"];' + "\n")
    for (i, j, k) in edge:
        # a -> b [label="xxx"];
        f.write(str(i) + ' -> ' + str(j) + ' [label="' + str(k) + '"];' + '\n')
    f.write("}")

    print(graphviz.Graph())
    # graph = pydot.graph_from_dot_file(location + '\\graph.dot')
    # graph = pydot.graph_from_dot_file(location + '\\graph.dot')
    # graph = graphviz.Source.from_file('graph.dot', location)
    # print(type(graph))
    # graph = graphviz.Source.from_file(location + '\\graph.dot')
    # from subprocess import check_call
    # check_call(['dot', '-Tpng', location + '\\graph.dot', '-o', location+'\\OutputFile.png'])
    # SHOW as an image
    # (graph,) = pydot.graph_from_dot_file(location + '\\graph.dot')
    # print(graph.render())

    # f_out = tempfile.NamedTemporaryFile(suffix=".png")
    # graph.write(f_out.name, format="png")
    # graph.render(graph)
    # Image.open(f_out.name).show()

    # document = open(location+'\\graph.dot')

    # graphs = pydot.graph_from_dot_data(document.read())
    # graph = graphs[0]


if __name__ == '__main__':
    main = tk.Tk()
    main.withdraw()

    file = filedialog.askopenfilename()
    tree = ET.parse(file)
    root = tree.getroot()

    # visualization()

    # ##### OUTPUT 2.3 #### #
    output_pos = prettytable.PrettyTable()
    output_iso = prettytable.PrettyTable()
    output_qsl = prettytable.PrettyTable()
    output_mtn = prettytable.PrettyTable()

    col_names = ['Part of Speech Tags', 'ISO Tags', 'QsLink Types', '5 most common Motion']
    pos = PoS()
    iso = ISO()
    qsl = Qs()
    mtn = motion()
    output_pos.add_column(col_names[0], [f'{key}: {values}' for key, values in pos.items()])
    output_iso.add_column(col_names[1], [f'{key}: {values}' for key, values in iso.items()])
    output_qsl.add_column(col_names[2], [f'{key}: {values}' for key, values in qsl.items()])
    output_mtn.add_column(col_names[3], [f'{key}: {values}' for key, values in mtn.items()])

    output_pos.align = 'l'
    output_iso.align = 'l'
    output_qsl.align = 'l'
    output_mtn.align = 'l'

    print(output_pos)
    print(output_iso)
    print(output_qsl)
    print(output_mtn)

    prep = prepositions()
    print('QsLinks prepositions', prep[0])
    print('Olinks prepositions', prep[1])
    print('All prepositions', prep[2])

    sentence_length()

    print('The DOT file will be generated, specify where to save it')
    save = filedialog.askdirectory()
    visualization(save)
