import json, glob
rows=[json.load(open(f)) for f in sorted(glob.glob('results/*/*/*/result.json'))]
order=['qwen3-coder-next','qwen3.8-27b','deepseek-v4-flash','glm-5.3']
for task in ['privacy','categories']:
    print(f"\n## {task}")
    for m in order:
        for r in [r for r in rows if r['model']==m and r['task']==task]:
            base=f"{m:18} #{r['rep']} {r['status']:7} {r['wall_s']:6.0f}s steps={r['steps']:3} in={r['tokens_in']/1e3:6.0f}k cache={r['tokens_cached']/1e3:5.0f}k out={r['tokens_out']/1e3:5.1f}k €{r['agent_cost_eur']:.3f} pytest={r['pytest_pass']} ruff={r['ruff_clean']} tests+={r['tests_added']} hookblocks={r['privacy_hook_blocks']} rawPII={r['raw_pii_in_agent_context']}"
            if task=='privacy':
                base+=f" | out={r.get('output_exists')} rows={r.get('rows')} email={r.get('remaining_email')} phone={r.get('remaining_phone')} url={r.get('remaining_url')} ent={r.get('html_entities_left')} idkept={r.get('raw_id_kept')} text={r.get('free_text_kept')}"
            else:
                base+=f" | out={r.get('output_exists')} n={r.get('n_categories')} schema={r.get('schema_ok')} llmpy={r.get('uses_project_llm')} fixed={r.get('uses_fixed_sample')}"
            print(base)
