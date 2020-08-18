# Dpredict
 
분석용? 딥러닝용? 둘다? (사용 형식 Restful API)

일단은 두가지 다 사용한다고 생각... (이를 고민하는 이유는 api를 2번 호출하는 과정 때문)
* API 최종 응답은 JSON으로 통일 -> 큰 문제없기 전에는 json형태로 return

프로세스
1. main은 flask로 API를 실행시키는 main.py

2. 딥러닝을 돌리는 py와 돌리지 않는 py 
2.1 딥러닝 모델을 compile을 할 경우 gpu를 사용함. 
main.py를 실행하면서 model은 미리 compile해야함. API를 호출할 경우마다 compile을 하면 gpu 메모리에 부하가 올 것이라고 생각함
(그러나, 딥러닝 모델이 몇개까지 compile이 가능한지 고려해야함)

2.2 돌리지 않는 경우 INPUT과 OUTPUT의 고민

추후 ppt로 class, py파일 용도 작성

