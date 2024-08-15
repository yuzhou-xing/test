import os,sys
import copy

# def error_message():


def read_vtt_info(vtt_path, flag_read_QA):
    single_vtt_info = {}
    flag_pattern = [False, False]
    flag_turn_part = False
    qa_info, qa_count = {},0
    turn_final = []
    question_info = {}
    # qa_pattern = [False, False, {}]
    # qa_pattern = [question_type, question,answer_list]
    qa_pattern = [False, False, False, {}]  #question_type, question, answer_flag, answer_list
    simple_pair = {}
    # flag_q = False
    single_question_info = {}
    with open(vtt_path, 'r', encoding='UTF8') as f:
        for i,line in enumerate(f):
            if '------------------------------' in line:
                flag_turn_part = True

            if not flag_turn_part:
                if i == 0:
                    if line.strip() == "WEBVTT":
                        continue
                    else:
                        print('第{}行格式错误'.format(i+1), vtt_path)
                        print('content:',line)
                        sys.exit()

                elif i == 1:
                    if line.strip() == ">":
                        continue
                    else:
                        print('第{}行格式错误'.format(i+1), vtt_path)
                        print('content:',line)
                        sys.exit()
                
                elif not line.strip():
                    continue

                elif '-->' in line.strip():
                    if not flag_pattern[0]:
                        flag_pattern[0] = line.strip()
                
                elif "</v>" in line.strip():
                    if flag_pattern[0] and not flag_pattern[1]:
                        flag_pattern[1] = line.strip()
                    turn_final.append(line.split('\t')[0].split(' ')[-1].replace('>',''))
                
                if flag_pattern[0] and flag_pattern[1]:
                    if flag_pattern[0] not in single_vtt_info:
                        single_vtt_info[flag_pattern[0]] = flag_pattern[1]
                        flag_pattern[0], flag_pattern[1] = False, False
                    else:
                        print('same time stamp in one file', flag_pattern[0],vtt_path)

            else:
                if '------------------------------' in line:
                    qa_count += 1
                    continue

                if not line.strip():
                    continue

                if qa_count == 1:
                    if line.strip() != 'Annotated Main Topics':
                        print('topic issue:', vtt_path, line.strip())
                        sys.exit()
                elif qa_count == 2:
                    if "Annotated Main Topics" not in qa_info:
                        qa_info["Annotated Main Topics"] = []
                    qa_info["Annotated Main Topics"].append(line.strip())
                    
                elif qa_count == 3:
                    if line.strip() != 'Queries and Annotated Summaries':
                        print('QA issue:', vtt_path, line.strip())
                        sys.exit()
                else:
                    if line.strip() == 'General Query:':
                        question_info['General Query'] = {}
                        qa_pattern[0] = 'General Query'
                    elif line.strip() == 'Specific Query:':
                        if qa_pattern[1] and (not qa_pattern[2]):
                            if qa_pattern[1] not in question_info[qa_pattern[0]]:
                                question_info[qa_pattern[0]][qa_pattern[1]] = qa_pattern[3]
                                qa_pattern[1] = False
                                qa_pattern[3] = {}
                            else:
                                print('line96 error')
                                sys.exit()
                        question_info['Specific Query'] = {}
                        qa_pattern[0] = 'Specific Query'
                    elif line.strip() == 'Simple Query:' or line.strip() == 'Simple Question:':
                        if qa_pattern[1] and (not qa_pattern[2]):
                            if qa_pattern[1] not in question_info[qa_pattern[0]]:
                                question_info[qa_pattern[0]][qa_pattern[1]] = qa_pattern[3]
                                qa_pattern[1] = False
                                qa_pattern[3] = {}
                            else:
                                print('line104 error')
                                sys.exit()
                        question_info['Simple Query'] = {}
                        qa_pattern[0] = 'Simple Query'

                    else:
                        if line.strip().lower().startswith('query') or line.strip().lower().startswith('question'):
                            if not qa_pattern[1]:
                                qa_pattern[1] = line.strip()
                                # qa_pattern[1] = line.strip().split(':')[0].split(' ',1)[-1]
                            elif not qa_pattern[2]:
                                # qa_pattern[1] = line.strip()
                                if qa_pattern[1] not in question_info[qa_pattern[0]]:
                                    question_info[qa_pattern[0]][qa_pattern[1]] = qa_pattern[3]
                                    qa_pattern[1] = line.strip()
                                    qa_pattern[3] = {}

                                else:
                                    print(vtt_path+ '包含的问题重复：'+ qa_pattern[0]+"\t"+qa_pattern[1]) 
                                    sys.exit()
                            else:
                                print('error in answer flag')
                                sys.exit()

                        elif line.strip().lower().startswith('answe'):
                            if qa_pattern[2]:
                                print('answer have no result')
                                print(vtt_path, line.strip())
                                sys.exit()
                            elif qa_pattern[1]:
                                qa_pattern[2] = line.strip()
                            else:
                                print('error1')
                                sys.exit()
                            
                        elif qa_pattern[1] and qa_pattern[2]:
                            if qa_pattern[2] not in qa_pattern[3]:
                                qa_pattern[3][qa_pattern[2]] = line.strip()
                                qa_pattern[2] = False
                            else:
                                print('error2')
                                sys.exit()
                        elif line.strip().lower().startswith('relevent') and ':' in line:
                            if not qa_pattern[2] and 'Relevent Text Spans' not in qa_pattern[3]:
                                qa_pattern[3]['Relevent Text Spans'] = line.strip()
                            else:
                                print('error in span')
                                sys.exit()


                    # if flag_q != question_info[list(question_info.keys())[-1]]:
                    #     question_info[flag_q] = {qa_pattern[0]:qa_pattern[2]}
                    #     qa_pattern = [False, False, {}]

    if flag_read_QA:
        if qa_pattern[3] and (qa_pattern[1] not in question_info[qa_pattern[0]]):
            question_info[qa_pattern[0]][qa_pattern[1]] = qa_pattern[3]
        else:
            print('line156 error')
            sys.exit()

    if "Queries and Annotated Summaries" not in qa_info:
        qa_info["Queries and Annotated Summaries"] = question_info

    if sorted(turn_final, key=int) != turn_final:
        print('turn的顺序有误',vtt_path)
        # print(sorted(turn_final, key=int))
        # print(turn_final)
        sys.exit()
    qa_info['all_turn'] = [int(x) for x in turn_final]

    if flag_read_QA:
        return single_vtt_info, qa_info
    else:
        return single_vtt_info




# input = r"E:\v-yuhangxing\data\FY24Q2-IS-Flexible-Data-Collection-TX\Meeting_QA_task\240814\data"
# output = r"E:\v-yuhangxing\data\FY24Q2-IS-Flexible-Data-Collection-TX\Meeting_QA_task\240814\output"
input = r"E:\Git_env_manage\solve_conflusion\test\work\data"
output = r"E:\Git_env_manage\solve_conflusion\test\work\out"

vtt_info = {}
for root1,der1,files1 in os.walk(input):
    for catalog_type in der1:
        for root,der, files in os.walk(os.path.join(root1,catalog_type)):
            for file in files:
                if file.endswith('vtt'):
                    if catalog_type not in vtt_info:
                        vtt_info[catalog_type] = {}
                    if file not in vtt_info[catalog_type]:
                        vtt_info[catalog_type][file] = os.path.join(root,file)    
    break


if (set(vtt_info["Annotated data"]) - set(vtt_info["Raw data to be annotated"])) and  (set(vtt_info["Raw data to be annotated"]) - set(vtt_info["Annotated data"])):
    print('vtt: annotated file and raw file not match')
    print('annotated file only:',list(set(vtt_info["Annotated data"]) - set(vtt_info["Raw data to be annotated"])))
    print('raw file only:',list(set(vtt_info["Raw data to be annotated"]) - set(vtt_info["Annotated data"])))

annotated_data_info = {}
annotated_qa_info = {}
raw_data_info = {}
for name, vtt_path in vtt_info['Annotated data'].items():
    annotated_data_info[name],annotated_qa_info[name] = read_vtt_info(vtt_path, True)
    raw_data_info[name] = read_vtt_info(vtt_info["Raw data to be annotated"][name],False)

#annotated_data_info -->   {filename:{timestamp:trans}}
#annotated_qa_info -->  {filename :{'Annotated Main Topics': [xx,xx], 'Queries and Annotated Summaries':{
        # General Query: {Q: {a1:xx, a2:xx}, Q: {a1:xx, a2:xx}},
        # Specific Query: {Q: {a1:xx, a2:xx, "Relevent Text Spans":xx }, Q: {a1:xx, a2:xx， "Relevent Text Spans":xx}},
        # Simple Query: {Q: {a1:xx, a2:xx}, Q: {a1:xx, a2:xx}}},
        #'all_turn': turn_final
# }}

# print(annotated_data_info)
# print(raw_data_info)
print(len(annotated_data_info),len(raw_data_info))
copy_annotated_data = copy.deepcopy(annotated_data_info)
for order_s, (name, single_pair) in enumerate(annotated_data_info.items()):
    for timeStamp,single_trans_c in single_pair.items():
        if single_trans_c.strip() == raw_data_info[name][timeStamp].strip():
            copy_annotated_data[name].pop(timeStamp)
            raw_data_info[name].pop(timeStamp)
        # else:
        #     with open(os.path.join(output,'ori_utts_differ.txt'),'a+', encodings="UTF8") as sav_ori:
        #         sav_ori.write('{}\t{}\t{}\n'.format(name, raw_data_info[name][timeStamp].strip(),single_trans_c.strip(),))

    if not copy_annotated_data[name]:
        copy_annotated_data.pop(name)
    if not raw_data_info[name]:
        raw_data_info.pop(name)
# if set(raw_data_info) - set(copy_annotated_data):
#     for
#     with open(os.path.join(output, 'ori_utts_differ.txt'), 'a+', encodings="UTF8") as sav_ori:
#         sav_ori.write('{}\t{}\t{}\n'.format(name, raw_data_info[name][timeStamp].strip(), single_trans_c.strip(), ))

print('annotated and raw 原始内容不对应的部分见：')
print('-'*20)
print('remain annotated data:',copy_annotated_data)
print('remain raw data:',raw_data_info)
print('-'*20)



#annotated_qa_info -->  {filename :{'Annotated Main Topics': [xx,xx], 'Queries and Annotated Summaries':{
        # General Query: {Q: {a1:xx, a2:xx}, Q: {a1:xx, a2:xx}},
        # Specific Query: {Q: {a1:xx, a2:xx, "Relevent Text Spans":xx }, Q: {a1:xx, a2:xx， "Relevent Text Spans":xx}},
        # Simple Query: {Q: {a1:xx, a2:xx}, Q: {a1:xx, a2:xx}},
        # 'all_turn': turn_final
copy_annotated_qa = copy.deepcopy(annotated_qa_info)
for order_qa,(name, qa_part) in enumerate(annotated_qa_info.items()):
    temp_turn_all = []
    for order_topic, main_topic in enumerate(qa_part['Annotated Main Topics']):
        print(main_topic)
        temp_turn = main_topic.strip().split(')')[0].split(' ')[-1].split('-')
        temp_turn = list(range(int(temp_turn[0]),int(temp_turn[1])+1))
        copy_annotated_qa[name]['all_turn'] = [x for x in annotated_qa_info[name]['all_turn'] if x not in temp_turn]
        if order_topic == len(enumerate(qa_part['Annotated Main Topics'])) -1 :
            and

#'Annotated Main Topics', 'Queries and Annotated Summaries', 'all_turn'