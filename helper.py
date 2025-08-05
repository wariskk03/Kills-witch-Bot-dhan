def get_input(message:str, data_type=str, valid_input:set=None, validator=None, show_valid:bool=True):
        while True:
            try:
                if show_valid:
                    input_data = input(f"\n{message}\n{valid_input if valid_input != None else ""} ").strip()
                else:
                    input_data = input(f"\n{message} ").strip()

                if validator:
                     return validator(input_data)
                
                input_data = data_type(input_data)

                if valid_input and input_data not in valid_input:
                    print(f"\nEnter Valid Input From {valid_input}")
                    continue
                
                return input_data
            
            except ValueError as e:
                print(f"\nError {e}")