import streamlit as st

DEBUG_FLAG = False


def dprint(*args, **kwargs):
    if DEBUG_FLAG:
        print(*args, **kwargs)


#
# def latex_to_expr(l_expr):
#     dprint("Test4-1: ",l_expr)
#     if (l_expr == None):
#         return "";
#
#     s:str = l_expr.strip()
#     s = s.replace(" ","");
#     s = s.replace("\\times","*");
#     end_var_values = {
#             "e" :["x","y","z","e","pi","\\"],
#             "pi":["x","y","z","e","pi","\\"],
#             "x" :["x","y","z","e","pi","\\"],
#             "y" :["x","y","z","e","pi","\\"],
#             "z" :["x","y","z","e","pi","\\"],
#             "0" :["x","y","z","e","pi","(","\\"],
#             "1" :["x","y","z","e","pi","(","\\"],
#             "2" :["x","y","z","e","pi","(","\\"],
#             "3" :["x","y","z","e","pi","(","\\"],
#             "4" :["x","y","z","e","pi","(","\\"],
#             "5" :["x","y","z","e","pi","(","\\"],
#             "6" :["x","y","z","e","pi","(","\\"],
#             "7" :["x","y","z","e","pi","(","\\"],
#             "8" :["x","y","z","e","pi","(","\\"],
#             "9" :["x","y","z","e","pi","(","\\"],
#             ")" :["x","y","z","e","pi","(","0","1","2","3","4","5","6","7","8","9","\\"]}
#
#     index = 0;
#     while index < len(s):
#         matched = False;
#         for k,v in end_var_values.items():
#             if ((s.startswith(k,index)) & (index+len(k) < len(s))):
#                 for t in v:
#                     if (t == "\\" and s.startswith(t+"right",index+len(k))):
#                         continue
#                     if (s.startswith(t,index+len(k))):
#                         matched=True;
#                         s = s[:index+len(k)] + "*" + s[index+len(k):];
#                         index+=1+len(k);
#                         break;
#
#         if (matched):
#             continue;
#         if (s.startswith("\\frac",index)):
#             matched = True;
#             # s = s[:index] + s[index + len("\\frac"):];
#             index += 5;
#             if (s[index] == "{"):
#                 # expexted {value}
#                 # FIRST {}
#                 inner_s, new_index = latex_extract_braced(s,index,"{");
#                 if (new_index == -1):
#                     return "";
#                 inner_s = latex_to_expr(inner_s);
#                 s = s[:index] + "{" + inner_s + "}" + s[new_index:];
#                 index = index + 2 + len(inner_s); # sets to last ")"
#                 # SECOND {}
#                 inner_s, new_index = latex_extract_braced(s,index,"{");
#                 if (new_index == -1):
#                     return "";
#                 inner_s = latex_to_expr(inner_s);
#                 s = s[:index] + "{" + inner_s + "}" + s[new_index:];
#                 index = index + 1 + len(inner_s); # sets to last ")"
#             else:
#                 # value is not in { }
#                 s = s[:index] + "{" + s[index] + "}"+ s[index+1:]
#                 index+=3;
#                 s = s[:index] + "{" + s[index] + "}"+ s[index+1:]
#                 index+=2; # sets to last ")"
#
#         if (matched):
#             continue;
#
#         index+=1;
#     return s;
#
# def latex_extract_braced(l_expr,start,brace):
#     """
#     extracts the value from the brace at the start index.
#
#     Args:
#         l_expr (str): The full expression
#         start (int): The index of "{"
#     """
#     endbrace = "}";
#     if (brace == "{"):
#         endbrace = "}";
#     elif (brace == "("):
#         endbrace = ")";
#     elif (brace == "["):
#         endbrace = "]";
#     else:
#         pass
#         # raise ValueError(f"ERROR 001, this should not happen")
#
#
#
#     if start >= len(l_expr) or l_expr[start] != brace:
#         st.write(f"Expected '{brace}' at position {start}")
#         return "", -1;
#
#     depth = 0
#     for i in range(start, len(l_expr)):
#         if l_expr[i] == brace:
#             depth += 1
#         elif l_expr[i] == endbrace:
#             depth -= 1
#             if depth == 0:
#                 return l_expr[start + 1:i], i + 1
#     st.write("Unmatched braces")
#
#     return "" , -1


def is_float(element):
    try:
        e = float(element)
        return e == e  # Checks for nan
    except ValueError:
        return False
