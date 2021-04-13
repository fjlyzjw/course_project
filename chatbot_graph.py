#!/usr/bin/env python3
# coding: utf-8
# File: chatbot_graph.py
# Reference: https://huangyong.github.io
# Recompose: zjw
# Date: 19-5-25

from question_classifier import *
from question_parser import *
from answer_search import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是小当家，请问今天想吃什么菜呢？'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        #print(res_classify)
        res_sql = self.parser.parser_main(res_classify)
        #print(res_sql)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = ChatBotGraph()
    print("输入回车键开始问答...")
    while 1:
        question = input('用户:')
        answer = handler.chat_main(question)
        print('小当家:', answer)


