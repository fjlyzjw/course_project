#!/usr/bin/env python3
# coding: utf-8
# File: question_parser.py
# Reference: https://huangyong.github.io
# Recompose: zjw
# Date: 19-5-25

class QuestionPaser:

    '''构建实体节点'''
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for typ in types:
                if typ not in entity_dict:
                    entity_dict[typ] = [arg]
                else:
                    entity_dict[typ].append(arg)

        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if question_type == 'dish_desc':
                sql = self.sql_transfer(question_type, entity_dict.get('dish'))

            elif question_type == 'mate_dish':
                sql = self.sql_transfer(question_type, entity_dict.get('materials'))

            elif question_type == 'no_mate_dish':
                sql = self.sql_transfer(question_type, entity_dict.get('materials'))

            elif question_type == 'tag_dish':
                sql = self.sql_transfer(question_type, entity_dict.get('tags'))

            elif question_type == 'no_tag_dish':
                sql = self.sql_transfer(question_type, entity_dict.get('tags'))

            elif question_type == 'cate_desc':
                sql = self.sql_transfer(question_type, entity_dict.get('cate'))

            elif question_type == 'dish_mate':
                sql = self.sql_transfer(question_type, entity_dict.get('dish'))

            elif question_type == 'func_dish':
                sql = self.sql_transfer(question_type, entity_dict.get('tags'))

            elif question_type == 'author_dish':
                sql = self.sql_transfer(question_type, entity_dict.get('author'))

            elif question_type == 'number_dish':
                sql = self.sql_transfer(question_type, entity_dict.get('tags'))


            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询菜的描述
        if question_type == 'dish_desc':
            sql = ["MATCH (m:dish) where m.name = '{0}' return m.name, m.score, m.heat, m.steps, m.tips, m.weburl".format(i) for i in entities]

        # 给材料查菜名
        elif question_type == 'mate_dish':
            sql1 = ["MATCH (m:dish)-[r:food_mat]->(n:materials) where (n.name = '{0}') return m.name, n.name".format(i) for i in entities]
            sql2 = ["MATCH (n:materials)-[r:mate_same]- () <-[p:food_mat]- (m:dish) where n.name = '{0}' return m.name, n.name".format(i) for i in entities]
            sql = sql1 + sql2

        # 给材料排除菜名
        elif question_type == 'no_mate_dish':
            sql = ["MATCH (m:dish)-[r:food_mat]->(n:materials) where (not n.name contains '{0}') return m.name, n.name".format(i) for i in entities]
            #sql2 = ["MATCH (n:materials)-[r:mate_same]- () <-[p:food_mat]- (m:dish) where n.name = '{0}' return m.name, n.name".format(i) for i in entities]
            

        # 给菜名查材料
        elif question_type == 'dish_mate' or question_type == 'number_dish':
            sql = ["MATCH (m:dish)-[r:food_mat]->(n:materials) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
        
        # 查询标签描述
        elif question_type == 'tag_dish':
            sql = ["MATCH (m:dish)-[r:dish_tag]->(n:tags) where n.name = '{0}' return m.name, n.name".format(i) for i in entities]

        # 查询否定标签描述
        elif question_type == 'no_tag_dish':
            sql = ["MATCH (m:dish)-[r:dish_tag]->(n:tags) where not(n.name = '{0}') return m.name, n.name".format(i) for i in entities]


        # 根据种类查询菜
        elif question_type == 'cate_desc':
            sql = ["MATCH (m:materials)-[r:mate_child]-> () <-[p:food_mat]- (n:dish) where m.name = '{0}' return m.name, n.name".format(i) for i in entities]

        # 查询菜的功效
        elif question_type == 'func_dish':
            sql = ["MATCH (m:dish)-[r:dish_tag]->(n:tags) where n.name = '{0}' return m.name, n.name".format(i) for i in entities]

        # 查询作者
        elif question_type == 'author_dish':
            sql = ["MATCH (m:dish)-[r:dish_author]->(n:author) where n.name = '{0}' return m.name, n.name".format(i) for i in entities]


        return sql



if __name__ == '__main__':
    handler = QuestionPaser().parser_main({'args': {'鱼': ['materials', 'cate']}, 'question_types': ['cate_desc']})
    print(handler)
