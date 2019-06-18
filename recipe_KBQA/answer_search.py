#!/usr/bin/env python3
# coding: utf-8
# File: answer_search.py
# reference: https://huangyong.github.io
# author:zjw
# Date: 18-10-5

from py2neo import Graph

class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            "bolt://localhost:7687",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="111111")
        self.num_limit = 100

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
            #print(final_answers)
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'dish_desc':
            subject = answers[0]['m.name']
            score = answers[0]['m.score']
            heat = answers[0]['m.heat']
            steps = answers[0]['m.steps']
            tips = answers[0]['m.tips']
            url = answers[0]['m.weburl']

            sql = "MATCH (m:dish)-[r:food_mat]->(n:materials) where m.name = '{0}' return m.name, r.name,r.quantity, n.name".format(subject)
            mat = self.g.run(sql).data()
            mat_desc = []
            for i in mat:
                if i['r.name'] == '食材':
                    mat_desc.append(i['n.name']+'   '+i['r.quantity'])
            final_answer = '{0}的做法：\n打分：{1}  有{2}个人做过\n所需材料：{3}\n步骤：{4} \n小贴士：{5} \n菜谱链接：{6}'.format(subject,score, heat ,'；\n'.join(list(set(mat_desc))[:self.num_limit]),steps,tips,url)

        elif question_type == 'mate_dish':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '食材{0}可以做的菜有：{1}\n请回复完整菜名获取详细菜谱'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'no_mate_dish':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '符合条件的的菜有：{0}\n请回复完整菜名获取详细菜谱'.format('；'.join(list(set(desc))[:self.num_limit]))


        elif question_type == 'tag_dish' :
            dish_name = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '符合{0}条件的菜有：{1}\n请回复完整菜名获取详细菜谱'.format(subject, '；'.join(list(set(dish_name))[:self.num_limit]))

        elif question_type == 'no_tag_dish' :
            dish_name = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '符合条件的菜有：{0}\n请回复完整菜名获取详细菜谱'.format('；'.join(list(set(dish_name))[:self.num_limit]))

        elif question_type == 'cate_desc':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0} 类别下的菜有：{1}\n请回复完整菜名获取详细菜谱'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'dish_mate':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0} 需要的材料有：{1}\n请回复完整菜名获取详细菜谱'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'func_dish':
            dish_name = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '有{0}作用的菜有：{1}\n请回复完整菜名获取详细菜谱'.format(subject, '；'.join(list(set(dish_name))[:self.num_limit]))

        elif question_type == 'author_dish':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '作者为{0}的菜有：{1}\n请回复完整菜名获取详细菜谱'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'number_dish':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '满足{0}条件的菜有：{1}道'.format(subject,  len(desc))

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()