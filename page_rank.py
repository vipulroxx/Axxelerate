#! /usr/bin/env python

import sys
import pymysql.cursors
import credentials
import pprint
from functools import partial
from multiprocessing import Pool

damping = 0.85

def main():

    pool = Pool(8)

    pp = pprint.PrettyPrinter(indent=4)

    connection = pymysql.connect(host = credentials.host,
                                 user = credentials.user,
                                 password = credentials.password,
                                 db = credentials.db,
                                 cursorclass = pymysql.cursors.DictCursor)

    nodes_and_ranks = None
    links = None


    with connection.cursor() as cursor:

        sql_hash_list = "SELECT `fromHash`, `toHash` FROM `linksTo`"
        sql_page_list = "SELECT `urlHash` FROM `pages`"

        cursor.execute(sql_page_list)
        original_from_db = cursor.fetchall()
        print("fetched first chunk")

        links = { row['urlHash'] : [] for row in original_from_db}

        cursor.execute(sql_hash_list)
        all_hashes = cursor.fetchall()

        for row in all_hashes:
            src = row['fromHash']
            dst = row['toHash']
            links[src].append(dst)

        print("fetched last chunk")

        nodes_and_ranks = {h: 0.15 for h in links}

        iteration = 0
        avg_diff = float("inf")

        while avg_diff > 0.00001:
            print("computing strengths")
            export_strengths_list = pool.map(partial(export_strength, prev_ranks=nodes_and_ranks, links=links), links)
            print("computed strengths, converting to dict")
            export_strengths = dict(export_strengths_list)


            print("computing new pageranks")
            new_ranks_list = pool.map(partial(compute_new_pr, export_strengths=export_strengths, links=links), links)

            print("converting new ranks to dict")
            new_ranks = dict(new_ranks_list)

            print("computing diffs")
            differences = []
            for node in new_ranks:
                diff =  abs(new_ranks[node] - nodes_and_ranks[node])
                differences.append(diff)
            print("computing average")
            avg_diff = sum(differences)/float(len(differences))
            nodes_and_ranks = new_ranks
            print("%s %s" % (iteration, avg_diff))
            iteration += 1

        print("start writing data")
        sql_update_result = "UPDATE `pages` SET `pagerank` = %s WHERE `urlHash` = %s"
        for h,rank in nodes_and_ranks.iteritems():
            cursor.execute(sql_update_result, (rank,h))
        print("done writing data")

    connection.commit()


def export_strength(node, prev_ranks, links):
    num_out = len(links[node])
    if num_out == 0:
        return [node, 0]
    else:
        return [node, prev_ranks[node] / num_out]

def compute_new_pr(node, export_strengths, links):
    contributions = 0
    for n in links:
        if node in links[n]:
            contributions += export_strengths[n]
    new_pr = (1 - damping) + (damping * contributions)
    return [node, new_pr]

if __name__ == "__main__":
    main()

