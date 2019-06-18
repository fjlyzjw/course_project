#!/usr/bin/env python3
# coding: utf-8
# File: question_classifier.py
# Reference: https://huangyong.github.io
# Recompose: zjw
# Date: 19-5-25

import os
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        #　特征词路径
        self.author_path = os.path.join(cur_dir, 'author.txt')
        self.dish_path = os.path.join(cur_dir, 'dish.txt')
        self.materials_path = os.path.join(cur_dir, 'materials.txt')
        self.tags_path = os.path.join(cur_dir, 'tags.txt')
        self.cate_path = os.path.join(cur_dir, 'child_food.txt')
        self.deny_path = os.path.join(cur_dir, 'deny.txt')
        # 加载特征词
        self.author_wds= [i.strip() for i in open(self.author_path) if i.strip()]
        self.dish_wds= [i.strip() for i in open(self.dish_path) if i.strip()]
        self.materials_wds= [i.strip() for i in open(self.materials_path) if i.strip()]
        self.tags_wds = [i.strip() for i in open(self.tags_path) if i.strip()]
        self.cate_wds = [i.strip()[0] for i in open(self.cate_path) if i.strip()]
        self.region_words = set(self.author_wds + self.dish_wds + self.materials_wds + self.tags_wds + self.cate_wds)
        self.deny_words = [i.strip() for i in open(self.deny_path) if i.strip()]
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        self.author_qwds = ['做过', '做了', '作者']
        self.dish_qwds = ['怎么做','菜名', '怎么', '有没有', '要怎么做', '咋做', '咋样做', '如何会', '菜', '这道菜', '步骤','菜谱']
        #给出材料问菜
        self.materials_qwds = ['可以', '用', '做什么', '有', '材料', '食材', '和','有哪些','能做什么','能够','用来','的做法']
        self.recomm_qwds = ['推荐', '最', '排名高', '很多人做', '火', '流行','普遍','受欢迎']
        self.func_qwds = ['吃什么好', '最好', '想要', '变', '有用','有效','什么好','什么菜']
        self.tag_qwds = ['的菜','有哪些菜','有哪些','是','口味','味','用时','快']
        #给出菜问材料
        self.dish_mate_qwds = ['哪些材料', '什么材料', '什么食材', '哪些食材', '啥食材', '啥材料', '需要什么','需要','要','准备啥','准备什么']
        #self.num_qwds = ['多少', '一共', '多少人', '数量', '是多少', '数', '多少个','多少道','有多少']
      

        print('model init finished ......')

        return

    '''分类主函数'''
    def classify(self, question):
        data = {}
        dish_dict = self.check_dish(question)
        if not dish_dict:
            return {}
        data['args'] = dish_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in dish_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        # 材料找菜&菜找材料
        if self.check_words(self.materials_qwds, question) and ('materials' in types):
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_type = 'no_mate_dish'
            else:
                question_type = 'mate_dish'
            question_types.append(question_type)

        if self.check_words(self.dish_mate_qwds, question) and ('dish' in types):
            question_type = 'dish_mate'
            question_types.append(question_type)

        #

        # 根据菜名
        if self.check_words(self.dish_qwds, question) and ('dish' in types):
            question_type = 'dish_desc'
            question_types.append(question_type)

        # 根据作者
        if self.check_words(self.author_qwds, question) and ('author' in types):
            question_type = 'author_dish'
            question_types.append(question_type)

        # 食物功效
        if self.check_words(self.func_qwds, question) and ('dish' in types):
            question_type = 'func_dish'
            question_types.append(question_type)

        # 标签描述
        if self.check_words(self.tag_qwds, question) and 'tags' in types:
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_type = 'no_tag_dish'
            else:
                question_type = 'tag_dish'
            question_types.append(question_type)


        # 标签描述
        if question_types == [] and ('tags' in types) and ('dish' not in types):
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_type = 'no_tag_dish'
            else:
                question_type = 'tag_dish'
            question_types.append(question_type)

        # 若没有查到相关的外部查询信息，那么则将该菜名信息返回
        if question_types == [] and 'dish' in types:
            question_types = ['dish_desc']

        # 若没有查到相关的外部查询信息，那么则将该菜名信息返回
        if question_types == [] and 'author' in types:
            question_types = ['author_dish']

        # 若没有查到相关的外部查询信息，那么则将该菜名信息返回
        if ('dish' not in types) and ('cate' in types):
            question_types = ['cate_desc']

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造词对应的类型'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.author_wds:
                wd_dict[wd].append('author')
            if wd in self.dish_wds:
                wd_dict[wd].append('dish')
            if wd in self.materials_wds:
                wd_dict[wd].append('materials')
            if wd in self.tags_wds:
                wd_dict[wd].append('tags')
            if wd in self.cate_wds:
                wd_dict[wd].append('cate')
        return wd_dict

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''
    def check_dish(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}
        #print(final_wds, final_dict)

        return final_dict

    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False

if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('输入你的问题:')
        data = handler.classify(question)
        print(data)