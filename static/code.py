import json

def run_task():
    print('Notifying the team about customer feedback...')
    result_dict = {'type': 'notify', 'data': "Customer reported a bad experience and requested feedback be sent to the owner/team regarding behavior, asking for improvement."}
    print(json.dumps(result_dict))
    return result_dict

if __name__ == '__main__':
    print('--- START run_task ---')
    try:
        result_dict = run_task()
        print('Action result:', json.dumps(result_dict))
    except Exception as e:
        print('Execution error inside run_task:', str(e))
    print('--- END run_task ---')
