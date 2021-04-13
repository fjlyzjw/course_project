#!/usr/bin/env python3
# coding: utf-8
# File: build_recipegraph.py
# Reference: https://huangyong.github.io
# Recompose: zjw
# Date: 19-5-25

import os
import json
from py2neo import Graph,Node

class RecipeGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/recipe.json')
        
        self.g = Graph(
            "bolt://localhost:7687",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="111111")
        

    '''读取文件'''
    def read_nodes(self):

        #共4类节点
        dishes = [] # 菜名
        materials = [] #　材料
        authors = [] # 作者
        tags = [] #标签
        
        dishes_infos = []

        #5种关系
        rels_food_mat = [] #菜名与食材的关系
        rels_author = [] #作者与菜名的关系
        rels_tag = [] #菜名与标签的关系
        
        mate_same = [] #同种食材不同名称的关系
        mate_child = [] #食材的子集


        count = 0
        for data in open(self.data_path):
            dish_dict = {}
            count += 1
            print(count)
            data_json = json.loads(data)
            dish = data_json['foodname']
            dish_dict['foodname'] = dish
            dishes.append(dish)

            author = data_json['author']
            dish_dict['author'] = author
            authors.append(author)

            dish_dict['score'] = ''
            dish_dict['heat'] = ''
            dish_dict['steps'] = ''
            dish_dict['tips'] = ''
            dish_dict['url'] = ''


            if 'mate' in data_json:
                mate = []
                for m in data_json['mate']:
                    tmp = m.replace('\n','')
                    if tmp == '':
                        continue
                    materials.append(tmp)
                    mate.append(tmp)
                
                quantity = data_json['quantity']
                
                weburi = data_json['uri']['uri']
                for num in range(len(mate)):
                    rels_food_mat.append([weburi, mate[num],quantity[num]])

            if 'tags' in data_json:
                tags += data_json['tags']
                weburi = data_json['uri']['uri']
                for tag in data_json['tags']:
                    rels_tag.append([weburi, tag])
                
            if 'author' in data_json:
                weburi = data_json['uri']['uri']
                author += data_json['author']
                rels_author.append([weburi, data_json['author']])


            #属性
            if 'score' in data_json:
                dish_dict['score'] = data_json['score']

            if 'tips' in data_json:
                dish_dict['tips'] = data_json['tips']

            if 'steps' in data_json:
                dish_dict['steps'] = data_json['steps']

            if 'heat' in data_json:
                dish_dict['heat'] = data_json['heat']

            if 'uri' in data_json:
                dish_dict['uri'] = data_json['uri']['uri']

            '''
            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail]
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                producers += producer
            '''
            dishes_infos.append(dish_dict)

        #同义词
        for line in open('sam_food.txt','r'):
            items = line.split('\t')
            #print(items)
            
            items[0] = items[0].replace('\n','')
            items[1] = items[1].replace('\n','')
            if items[0] != '' and items[1] != '':
                materials += items
                mate_same.append([items[0], items[1]])
            #mate_same.append([items[1], items[0]])

        for line in open('child_food.txt'):
            items = line.split('\t')
            #print(items)
            tmplist = []
            for item in items:
                item = item.replace('\n','')
                if item == '':
                    continue
                else:
                    tmplist.append(item)
            materials += tmplist
            for i in tmplist[1:]:
                mate_child.append([items[0], i])

        #print(mate_same)
        #print(mate_child)
        return set(dishes), set(materials), set(tags), set(authors), dishes_infos,\
               rels_food_mat, rels_author, rels_tag, mate_same, mate_child

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return

    '''创建知识图谱中心的节点'''
    def create_recipe_nodes(self, dishes_infos):
        count = 0
        for dish_dict in dishes_infos:
            node = Node('dish', name=dish_dict['foodname'], score=dish_dict['score'],
                        heat=dish_dict['heat'] ,steps=dish_dict['steps'],
                        tips=dish_dict['tips'], weburl = dish_dict['uri'])

            self.g.create(node)
            count += 1
            print(count)
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        dishes, materials, tags, author, dishes_infos, rels_food_mat, rels_author, rels_tag, mate_same, mate_child = self.read_nodes()
        self.create_recipe_nodes(dishes_infos)
        #self.create_node('dishes', dishes)
        #print(len(dishes))
        self.create_node('materials', materials)
        print(len(materials))
        self.create_node('tags', tags)
        print(len(tags))
        self.create_node('author', author)
        print(len(author))
        return


    '''创建实体关系边'''
    def create_graphrels(self):
        dishes, materials, tags, author, dishes_infos, rels_food_mat, rels_author, rels_tag, mate_same, mate_child = self.read_nodes()
        self.create_mat_relationship('dish', 'materials', rels_food_mat, 'food_mat', '食材',)
        self.create_dish_relationship('dish', 'author', rels_author, 'dish_author', '作者')
        self.create_dish_relationship('dish', 'tags', rels_tag, 'dish_tag', '标签')
        self.create_relationship('materials', 'materials', mate_same, 'mate_same', '材料同义')
        self.create_relationship('materials', 'materials', mate_child, 'mate_child', '材料子集')
       

        '''创建实体有向边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

        '''创建与菜相关的关联边'''
    def create_dish_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.weburl='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

        '''创建材料关联边'''
    def create_mat_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            quan = edge[2]
            query = "match(p:%s),(q:%s) where p.weburl='%s'and q.name='%s' create (p)-[rel:%s{name:'%s', quantity:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name, quan)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''导出数据'''

    def export_data(self):
        dishes, materials, tags, author, dishes_infos, rels_food_mat, rels_author, rels_tag, mate_same, mate_child = self.read_nodes()

        f_author = open('author.txt', 'w+')
        f_tags = open('tags.txt', 'w+')
        f_materials = open('materials.txt', 'w+')
        f_dish = open('dish.txt', 'w+')

        f_author.write('\n'.join(list(author)))
        f_tags.write('\n'.join(list(tags)))
        listmate = list(materials)
        for i in listmate:
            if i is None:
                listmate.remove(i)
        f_materials.write('\n'.join(listmate))
        f_dish.write('\n'.join(list(dishes)))

        f_author.close()
        f_tags.close()
        f_materials.close()
        f_dish.close()

        return
    


if __name__ == '__main__':
    handler = RecipeGraph()
    #handler.export_data()
    handler.create_graphnodes()
    handler.create_graphrels()
