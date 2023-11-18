import os

from pymongo import MongoClient
from dotenv import load_dotenv

# MongoDB Connection
load_dotenv()
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')
mongoClient = MongoClient(mongo_connection_string)

# Clear the MongoDB collection
musicDB = mongoCollection = mongoClient['Music']['Merge'] 

BGM_ranking =[]

musicDate = list(musicDB.find())

for item in musicDate:
    melon_rank = item.get('Melon_rank', 0)
    bugs_rank = item.get('Bugs_rank', 0)
    genie_rank = item.get('Genie_rank', 0)

    BGM_ranking.append([melon_rank, bugs_rank, genie_rank])

# 각 행의 숫자들을 정렬하되 0은 뒤에 위치하게 하는 함수
def custom_sort_row(ranking):
    nonzero_values = sorted([val for val in ranking if val != 0])
    zeros = [0] * (len(ranking) - len(nonzero_values))
    return nonzero_values + zeros


# 각 차트별 가중치 계산
def convertRank(sorted_ranking):
    convertRank = []
    for row in sorted_ranking:
        divRank = []
        # 숫자 1-10까지의 랭크 부여
        for rank in row:
            if rank == 0:
                divRank.append(0)
            elif rank % 10 != 0:
                divRank.append((rank // 10) + 1)
            else:  
                divRank.append(rank // 10)
                
        convertRank.append(divRank)
        
    return convertRank

def cal_D(convertRank):

    temp_result = []  # 결과를 저장할 리스트
    
    for row in convertRank:
        num_zeros = row.count(0)  # 0의 갯수를 세기
        max_difference = 0  # 가장 큰 편차를 저장할 변수
        max_difference_idx = None  # 가장 큰 편차의 인덱스를 저장할 변수

        for i in range(len(row)):
            for j in range(i + 1, len(row)):
                if row[i] != 0 and row[j] != 0:
                    difference = abs(row[j] - row[i])  # 편차 계산
                    if difference > max_difference:
                        max_difference = difference
                        max_difference_idx = i

        if max_difference_idx is not None:
            # 최대 편차의 인덱스를 사용하여 연산 수행
            score = num_zeros * 30 + max_difference * 5
        else:
            # 모든 값이 0이거나 한 행에 값이 없을 경우 0으로 처리
            score = 0

        # 0이 두 개인 경우
        if num_zeros == 2:
            score += 60  # 기본값 60 더하기

        # 0이 두 개 이상이면서 나머지 값이 0이 아닌 경우
        if num_zeros >= 2 and any(val != 0 for val in row):
            non_zero_val = [val for val in row if val != 0][0]
            score += non_zero_val * 5
        temp_result.append(score)
    
    return temp_result

    

#부여된 우선순위를 포함하여 최종우선순위 계산
def calculate_final_ranking(sorted_ranking):
    resultArr = []

    for arr in sorted_ranking:
        # 배열의 첫 3개 요소 중 0이 아닌 값을 추출
        non_zero_values = [value for value in arr[:3] if value != 0]
        if non_zero_values:
            # 0이 아닌 값들의 평균을 계산하고 소수점 3자리까지 반올림
            avg = round(sum(non_zero_values) / len(non_zero_values), 3)

            #디버깅용
            print(avg,arr[3])

            # 최종 순위를 계산하여 결과 배열에 추가
            result = avg + arr[3]

        #없는 노래의 경우(예외처리)
        else:
            result = arr[3]
        resultArr.append(result)

    return resultArr


#디버깅용 (주어진 배열)
print(BGM_ranking)

# sample 배열 정렬
sorted_ranking = [custom_sort_row(row) for row in BGM_ranking]

#디버깅용 (정렬된 배열)
print(sorted_ranking)

#정렬된 배열 Rank별로 숫자 부여
converted_ranking = convertRank(sorted_ranking)  # 변수 이름을 'converted_ranking'으로 수정

#디버깅용 (우선순위 부여된 배열)
print(converted_ranking)

#각 노래별 우선순위 계산
temp_result = cal_D(converted_ranking)  

#디버깅용 (우선순위만 담긴 배열)
print(temp_result)

#우선순위 정렬된 배열에 추가
for i, row in enumerate(sorted_ranking):
    row.append(temp_result[i])

# 디버깅용 (sorted_ranking에 우선순위 추가 후)
print(sorted_ranking)


#최종계산
final_result = calculate_final_ranking(sorted_ranking)

#디버깅용
print(final_result)

# 1. `final_rankings` 값을 각 문서에 저장합니다.
for i, rank in enumerate(final_result):
    musicDB.update_one({'_id': musicDate[i]['_id']}, {'$set': {'final_ranking': rank}})

# 2. `Merge` 컬렉션의 모든 문서를 `final_ranking` 필드를 기준으로 정렬하여 가져옵니다.
sorted_documents = list(musicDB.find().sort('final_ranking'))

# 3. `Merge` 컬렉션을 삭제하고 정렬된 문서를 다시 삽입합니다.
musicDB.drop()
musicDB.insert_many(sorted_documents)

