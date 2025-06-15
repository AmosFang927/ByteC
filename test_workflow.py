import json

with open('weekly_report_workflow.json') as f:
    wf = json.load(f)

nodes = {node['name']: node for node in wf.get('nodes', [])}

assert 'Cron' in nodes, 'Cron node missing'
cron_params = nodes['Cron']['parameters']
cron_expr = cron_params['triggerTimes']['item'][0]['cronExpression']
assert cron_expr == '0 9 * * 1', f'Cron expression incorrect: {cron_expr}'

for required in ['Read Sheet', 'Process Data', 'Log Output', 'Write Sheet']:
    assert required in nodes, f'{required} node missing'

print('All tests passed.')
