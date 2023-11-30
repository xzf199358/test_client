SELECT test_time, sig_value FROM public.original_signal
where struct_type_id in (SELECT id FROM public.struct_type where test_name ={test_name});