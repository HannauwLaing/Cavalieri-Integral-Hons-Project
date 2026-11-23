use std::{
    collections::HashMap,
    f64::consts::{E, PI},
    fmt::format,
    ops::{Add, Div, Mul, Neg, Sub},
};

use nom::{
    branch::alt, bytes::complete::tag, character::complete::alpha1, combinator::verify,
    error::Error, multi::fold_many0, number::complete::double, IResult,
};

use crate::errors::ParsedFuncError;

use super::differentiable::AD;

use rust_latex_parser::{parse_equation, EqNode};

#[derive(Clone)]
pub struct NamedUnaryOp<'a, T> {
    pub name: String,
    pub func: &'a dyn Fn(T) -> T,
}

#[derive(Clone)]
pub struct NamedBinaryOp<'a, T> {
    pub name: String,
    pub func: &'a dyn Fn(T, T) -> T,
}

pub enum Expr<'a, const I: usize, T> {
    Var(usize),
    Const(T),
    UOp(Box<Expr<'a, I, T>>, NamedUnaryOp<'a, T>),
    BiOp(
        Box<Expr<'a, I, T>>,
        Box<Expr<'a, I, T>>,
        NamedBinaryOp<'a, T>,
    ),
    Powi(Box<Expr<'a, I, T>>, i32),
}

pub trait BasicArithmetic:
    Add<Self, Output = Self>
    + Sub<Self, Output = Self>
    + Mul<Self, Output = Self>
    + Div<Self, Output = Self>
    + Neg<Output = Self>
    + Clone
    + Sized
{
    fn pow(self, rhs: Self) -> Self;
    fn powi(self, n: i32) -> Self;
}

impl<'a, const I: usize, T: BasicArithmetic> Expr<'a, I, T> {
    pub fn eval(&self, pars: &[T; I]) -> T {
        match self {
            Expr::Const(c) => c.clone(),
            Expr::Var(i) => pars[*i].clone(),
            Expr::UOp(inner, NamedUnaryOp { name, func }) => func(inner.eval(pars)),
            Expr::BiOp(inner1, inner2, NamedBinaryOp { name, func }) => {
                func(inner1.eval(pars), inner2.eval(pars))
            }
            Expr::Powi(inner, exponent) => inner.eval(pars).powi(*exponent),
        }
    }

    pub fn safe_eval(&self, pars: &[T; I]) -> Option<T> {
        match self {
            Expr::Const(c) => Some(c.clone()),
            Expr::Var(i) => pars.get(*i).cloned(),
            Expr::UOp(inner, NamedUnaryOp { name, func }) => inner.safe_eval(pars).map(|x| func(x)),
            Expr::BiOp(inner1, inner2, NamedBinaryOp { name, func }) => inner1
                .safe_eval(pars)
                .zip(inner2.safe_eval(pars))
                .map(|(x1, x2)| func(x1, x2)),
            Expr::Powi(inner, exponent) => inner.safe_eval(pars).map(|x| x.powi(*exponent)),
        }
    }
}

pub trait ArithParsable: BasicArithmetic + From<f64> {}

fn parse_parenth<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
    context: &HashMap<String, ContextElement<'a, T>>,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    let expr = match tag::<_, _, Error<&str>>("(")(expr) {
        Ok((expr, _)) => expr,
        Err(e) => return Err(e.map(|_| format!("No opening parenthesis found at: '...{}'", expr))),
    };
    let (expr, res) = parse_expression(expr, context)?;
    let expr = match tag::<_, _, Error<&str>>(")")(expr) {
        Ok((expr, _)) => expr,
        Err(e) => return Err(e.map(|_| format!("No closing parenthesis found at: '...{}'", expr))),
    };
    Ok((expr, res))
}

fn parse_neg_count(expr: &str) -> IResult<&str, usize> {
    fold_many0(tag("-"), || 0usize, |accu, _| (accu + 1))(expr)
}

fn parse_name(expr: &str) -> IResult<&str, &str, String> {
    match alpha1::<_, Error<&str>>(expr) {
        Ok(v) => Ok(v),
        Err(e) => Err(e.map(|_| format!("Could not find a valid name at '...{}'", expr))),
    }
}

fn parse_func<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
    context: &HashMap<String, ContextElement<'a, T>>,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    let (expr, name) = parse_name(expr)?;

    let func = match context.get(name) {
        Some(ContextElement::UOp(f)) => (*f).clone(),
        _ => {
            return Err(nom::Err::Error(format!(
                "No unary operator with name '{name}' exists"
            )));
        }
    };

    let expr = match tag::<_, _, Error<&str>>("(")(expr) {
        Ok((expr, _)) => expr,
        Err(e) => {
            return Err(e.map(|_| {
                format!("Expected function '{name}' opening parenthesis at '...{expr}'")
            }));
        }
    };
    let (expr, res) = parse_expression(expr, context)?;
    let expr = match tag::<_, _, Error<&str>>(")")(expr) {
        Ok((expr, _)) => expr,
        Err(e) => {
            return Err(e.map(|_| {
                format!("Expected function '{name}' closing parenthesis at '...{expr}'")
            }));
        }
    };
    Ok((
        expr,
        Expr::UOp(
            Box::new(res),
            NamedUnaryOp {
                name: name.to_owned(),
                func: func,
            },
        ),
    ))
}

fn parse_var<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
    context: &HashMap<String, ContextElement<'a, T>>,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    let (expr, name) = parse_name(expr)?;

    let res = match context.get(name) {
        Some(ContextElement::Const(x)) => Expr::Const(x.clone()),
        Some(ContextElement::Var(i)) => Expr::Var(*i),
        _ => {
            return Err(nom::Err::Error(format!(
                "No variable or parameter with name '{name}' exists"
            )))
        }
    };

    Ok((expr, res))
}

fn parse_const<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    match double::<_, Error<&str>>(expr) {
        Ok((expr, c)) => Ok((expr, Expr::Const(T::from(c)))),
        _ => return Err(nom::Err::Error(format!("Error parsing f64 at '...{expr}'"))),
    }
}

fn parse_pow<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
    context: &HashMap<String, ContextElement<'a, T>>,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    let expr = match tag::<_, _, Error<&str>>("^")(expr) {
        Ok((expr, _)) => expr,
        Err(_) => {
            return Err(nom::Err::Error(format!(
                "Missing exponentiation sign '^' at '...{expr}'"
            )))
        }
    };
    parse_term(expr, context, true)
}

fn parse_powi<'a>(expr: &'a str) -> IResult<&'a str, i32, String> {
    let expr = match tag::<_, _, Error<&str>>("**")(expr) {
        Ok((expr, _)) => expr,
        Err(_) => {
            return Err(nom::Err::Error(format!(
                "Missing integer exponentiation sign '**' at '...{expr}'"
            )));
        }
    };
    nom::character::complete::i32::<_, Error<&str>>(expr)
        .map_err(|_| nom::Err::Error(format!("Could not build a valid i32 at '...{expr}'")))
}

fn parse_term<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
    context: &HashMap<String, ContextElement<'a, T>>,
    allow_neg: bool,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    let (expr, negations) = match verify(parse_neg_count, |negations| {
        *negations == 0 || (allow_neg && *negations == 1)
    })(expr)
    {
        Ok(v) => v,
        Err(e) => return Err(e.map(|_| format!("Too many negations at: '...{}'", expr))),
    };

    let mut ex_term = parse_parenth(expr, context)
        .or_else(|_| parse_const(expr))
        .or_else(|_| parse_func(expr, context))
        .or_else(|_| parse_var(expr, context))
        .map_err(|_| nom::Err::Error(format!("Error parsing singular term at '...{expr}'")))?;

    // Exponentiation
    if let Ok((expr, exponent)) = parse_pow(ex_term.0, context) {
        ex_term.0 = expr;
        ex_term.1 = Expr::BiOp(
            Box::new(ex_term.1),
            Box::new(exponent),
            NamedBinaryOp {
                name: "power".to_owned(),
                func: &T::pow,
            },
        );
    } else if let Ok((expr, exponent)) = parse_powi(ex_term.0) {
        ex_term.0 = expr;
        ex_term.1 = Expr::Powi(Box::new(ex_term.1), exponent);
    }

    // Negation
    if negations == 1 {
        ex_term.1 = Expr::UOp(
            Box::new(ex_term.1),
            NamedUnaryOp {
                name: "Neg".to_owned(),
                func: &T::neg,
            },
        );
    }
    Ok(ex_term)
}

fn parse_terms_mul<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
    context: &HashMap<String, ContextElement<'a, T>>,
    allow_neg: bool,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    let mut ex_terms = parse_term(expr, context, allow_neg)?;
    while let Ok((nexpr, op)) = alt::<_, _, Error<&str>, _>((tag("*"), tag("/")))(ex_terms.0) {
        let ex_term = parse_term(nexpr, context, true)?;
        let func: &dyn Fn(T, T) -> T = match op {
            "*" => &T::mul,
            "/" => &T::div,
            _ => unreachable!(),
        };
        ex_terms.0 = ex_term.0;
        ex_terms.1 = Expr::BiOp(
            Box::new(ex_terms.1),
            Box::new(ex_term.1),
            NamedBinaryOp {
                name: op.to_owned(),
                func: func,
            },
        );
    }
    Ok(ex_terms)
}

fn parse_expression<'a, 'b, const I: usize, T: ArithParsable>(
    expr: &'b str,
    context: &HashMap<String, ContextElement<'a, T>>,
) -> IResult<&'b str, Expr<'a, I, T>, String> {
    let mut ex_terms = parse_terms_mul(expr, context, true)?;
    while let Ok((nexpr, op)) = alt::<_, _, Error<&str>, _>((tag("+"), tag("-")))(ex_terms.0) {
        let ex_term = parse_terms_mul(nexpr, context, false)?;
        let func: &dyn Fn(T, T) -> T = match op {
            "+" => &T::add,
            "-" => &T::sub,
            _ => unreachable!(),
        };
        ex_terms.0 = ex_term.0;
        ex_terms.1 = Expr::BiOp(
            Box::new(ex_terms.1),
            Box::new(ex_term.1),
            NamedBinaryOp {
                name: op.to_owned(),
                func: func,
            },
        );
    }
    Ok(ex_terms)
}

pub enum ContextElement<'a, T: ArithParsable> {
    Const(T),
    Var(usize),
    UOp(&'a dyn Fn(T) -> T),
}

/// Creates an executable expression from text input.
///
/// * `expr` - The expression
/// * `context` - The expressaion context
pub fn compile_expression<'a, const I: usize, T: ArithParsable>(
    expr: &str,
    context: impl AsRef<HashMap<String, ContextElement<'a, T>>>,
) -> Result<Expr<'a, I, T>, ParsedFuncError> {
    for (name, ce) in context.as_ref() {
        if let ContextElement::Var(i) = ce {
            if *i >= I {
                return Err(ParsedFuncError::ParameterOutOfBounds(
                    name.to_string(),
                    *i,
                    I,
                ));
            }
        }
    }
    let mut expr = expr.to_string();

    expr.retain(|c| !c.is_whitespace());
    let term = parse_expression(&expr, context.as_ref())?;
    if !term.0.is_empty() {
        return Err(ParsedFuncError::ResidueError(term.0.to_string()));
    }
    Ok(term.1)
}

fn parse_2_elem_f64_arr<'a>(
    expr: &'a str,
    context: &HashMap<String, ContextElement<f64>>,
) -> IResult<&'a str, [f64; 2], String> {
    let expr = match tag::<_, _, Error<&str>>("[")(expr) {
        Ok((expr, _)) => expr,
        Err(e) => return Err(e.map(|_| format!("Expected opening brakcet at: '...{}'", expr))),
    };
    let (expr, v1) = parse_expression::<0, _>(expr, context)?;

    let expr = match tag::<_, _, Error<&str>>(",")(expr) {
        Ok((expr, _)) => expr,
        Err(e) => return Err(e.map(|_| format!("Expected comma at: '...{}'", expr))),
    };
    let (expr, v2) = parse_expression::<0, _>(expr, context)?;
    let expr = match tag::<_, _, Error<&str>>("]")(expr) {
        Ok((expr, _)) => expr,
        Err(e) => return Err(e.map(|_| format!("Expected closing bracket at: '...{}'", expr))),
    };
    Ok((expr, [v1.eval(&[]), v2.eval(&[])]))
}

fn parse_list_of_elem<'a, T>(
    expr: &'a str,
    elem_parser: impl Fn(&'a str) -> IResult<&'a str, T, String>,
    require_brackets: bool,
) -> IResult<&str, Vec<T>, String> {
    let expr = if require_brackets {
        match tag::<_, _, Error<&str>>("[")(expr) {
            Ok((expr, _)) => expr,
            Err(e) => return Err(e.map(|_| format!("Expected opening brakcet at: '...{}'", expr))),
        }
    } else {
        expr
    };
    let (mut expr, v) = elem_parser(expr)?;
    let mut elems = vec![v];

    while let Ok((nexpr, _)) = tag::<_, _, Error<&str>>(",")(expr) {
        let (nexpr, v) = elem_parser(nexpr)?;
        expr = nexpr;
        elems.push(v);
    }
    let expr = if require_brackets {
        match tag::<_, _, Error<&str>>("]")(expr) {
            Ok((expr, _)) => expr,
            Err(e) => return Err(e.map(|_| format!("Expected closing brakcet at: '...{}'", expr))),
        }
    } else {
        expr
    };
    Ok((expr, elems))
}

/// Creates an interval set from text input.
///
/// * `expr` - The interval set expression
/// * `context` - The expression context
pub fn compile_interval_list<'a, 'b>(
    expr: &'a str,
    context: impl AsRef<HashMap<String, ContextElement<'b, f64>>>,
) -> Result<Vec<[f64; 2]>, ParsedFuncError> {
    let mut expr = expr.to_string();
    expr.retain(|c| !c.is_whitespace());
    let (expr, list) = parse_list_of_elem(
        &expr,
        |expr| parse_2_elem_f64_arr(expr, context.as_ref()),
        false,
    )?;
    if !expr.is_empty() {
        return Err(ParsedFuncError::ResidueError(expr.to_string()));
    }
    Ok(list)
}

/// Creates a polygon set from text input.
///
/// * `expr` - The polygon set expression
/// * `context` - The expression context
pub fn compile_polygon_set<'a, 'b>(
    expr: &'a str,
    context: impl AsRef<HashMap<String, ContextElement<'b, f64>>>,
) -> Result<Vec<Vec<[f64; 2]>>, ParsedFuncError> {
    let mut expr = expr.to_string();
    expr.retain(|c| !c.is_whitespace());
    let (expr, list) = parse_list_of_elem(
        &expr,
        |expr| {
            parse_list_of_elem(
                expr,
                |expr| parse_2_elem_f64_arr(expr, context.as_ref()),
                true,
            )
        },
        false,
    )?;
    if !expr.is_empty() {
        return Err(ParsedFuncError::ResidueError(expr.to_string()));
    }
    Ok(list)
}

impl BasicArithmetic for AD {
    fn pow(self, rhs: Self) -> Self {
        self.pow(rhs)
    }

    fn powi(self, n: i32) -> Self {
        self.powi(n)
    }
}
impl ArithParsable for AD {}

impl BasicArithmetic for f64 {
    fn pow(self, rhs: Self) -> Self {
        self.powf(rhs)
    }

    fn powi(self, n: i32) -> Self {
        f64::powi(self, n)
    }
}
impl ArithParsable for f64 {}

pub struct DefaultContext<'a, T: ArithParsable>(HashMap<String, ContextElement<'a, T>>);

impl<'a, T: ArithParsable> DefaultContext<'a, T> {
    pub fn add_var(&mut self, name: &str, loc: usize) {
        self.0.insert(name.to_string(), ContextElement::Var(loc));
    }

    pub fn add_const(&mut self, name: &str, val: T) {
        self.0.insert(name.to_string(), ContextElement::Const(val));
    }

    pub fn add_func(&mut self, name: &str, func: &'a dyn Fn(T) -> T) {
        self.0.insert(name.to_string(), ContextElement::UOp(func));
    }
}

impl<'a, T: ArithParsable> AsRef<HashMap<String, ContextElement<'a, T>>> for DefaultContext<'a, T> {
    fn as_ref(&self) -> &HashMap<String, ContextElement<'a, T>> {
        &self.0
    }
}

/* `DefaultContext` implementations*/

impl<'a> Default for DefaultContext<'a, AD> {
    fn default() -> Self {
        let ops: [(&str, ContextElement<'a, AD>); 18] = [
            ("pi", ContextElement::Const(AD(PI, 0f64))),
            ("e", ContextElement::Const(AD(E, 0f64))),
            ("abs", ContextElement::UOp(&AD::abs)),
            ("sin", ContextElement::UOp(&AD::sin)),
            ("cos", ContextElement::UOp(&AD::cos)),
            ("tan", ContextElement::UOp(&AD::tan)),
            ("asin", ContextElement::UOp(&AD::asin)),
            ("acos", ContextElement::UOp(&AD::acos)),
            ("atan", ContextElement::UOp(&AD::atan)),
            ("ln", ContextElement::UOp(&AD::ln)),
            ("exp", ContextElement::UOp(&AD::exp)),
            ("sqrt", ContextElement::UOp(&AD::sqrt)),
            ("sinh", ContextElement::UOp(&AD::sinh)),
            ("cosh", ContextElement::UOp(&AD::cosh)),
            ("tanh", ContextElement::UOp(&AD::tanh)),
            ("asinh", ContextElement::UOp(&AD::asinh)),
            ("acosh", ContextElement::UOp(&AD::acosh)),
            ("atanh", ContextElement::UOp(&AD::atanh)),
        ];
        let context =
            HashMap::from_iter(ops.into_iter().map(|(name, func)| (name.to_string(), func)));
        Self(context)
    }
}

impl<'a> Default for DefaultContext<'a, f64> {
    fn default() -> Self {
        let ops: [(&str, ContextElement<'a, f64>); 18] = [
            ("pi", ContextElement::Const(PI)),
            ("e", ContextElement::Const(E)),
            ("abs", ContextElement::UOp(&f64::abs)),
            ("sin", ContextElement::UOp(&f64::sin)),
            ("cos", ContextElement::UOp(&f64::cos)),
            ("tan", ContextElement::UOp(&f64::tan)),
            ("asin", ContextElement::UOp(&f64::asin)),
            ("acos", ContextElement::UOp(&f64::acos)),
            ("atan", ContextElement::UOp(&f64::atan)),
            ("ln", ContextElement::UOp(&f64::ln)),
            ("exp", ContextElement::UOp(&f64::exp)),
            ("sqrt", ContextElement::UOp(&f64::sqrt)),
            ("sinh", ContextElement::UOp(&f64::sinh)),
            ("cosh", ContextElement::UOp(&f64::cosh)),
            ("tanh", ContextElement::UOp(&f64::tanh)),
            ("asinh", ContextElement::UOp(&f64::asinh)),
            ("acosh", ContextElement::UOp(&f64::acosh)),
            ("atanh", ContextElement::UOp(&f64::atanh)),
        ];
        let context =
            HashMap::from_iter(ops.into_iter().map(|(name, func)| (name.to_string(), func)));
        Self(context)
    }
}

pub fn compile_latex_expression<'a, const I: usize, T: ArithParsable>(
    latex: &str,
    context: impl AsRef<HashMap<String, ContextElement<'a, T>>>,
) -> Result<Expr<'a, I, T>, ParsedFuncError> {
    let expr_ast = parse_equation(latex);

    let expr_str = ast_to_plain_string(&expr_ast);
    return compile_expression(&expr_str, context);
}

fn ast_to_plain_string(node: &EqNode) -> String {
    match node {
        EqNode::Text(s) => normalise_text(s),

        EqNode::Space(_) => " ".to_string(),

        EqNode::Seq(nodes) => seq_to_plain_string(nodes),

        EqNode::Frac(num, den) => {
            let num = ast_to_plain_string(num);
            let den = ast_to_plain_string(den);
            if num.len() == 2 && den.is_empty() {
                let chars: Vec<char> = num.chars().collect();
                format!("(({})/({}))", chars[0], chars[1])
            } else {
                format!("(({})/({}))", num, den)
            }
        }
        EqNode::Sup(base, exp) => {
            let base = ast_to_plain_string(base);
            let exp = ast_to_plain_string(exp);
            // if ast_to_plain_string(base).ends_with(")") {
            //     println!(
            //         "Test2-1: {}^({})",
            //         ast_to_plain_string(base),
            //         ast_to_plain_string(exp)
            //     );
            // } else {
            //     println!(
            //         "Test2-2: ({})^({})",
            //         ast_to_plain_string(base),
            //         ast_to_plain_string(exp)
            //     );
            // }

            if base.ends_with(")") {
                format!("{}^({})", base, exp)
            } else {
                format!("(({})^({}))", base, exp)
            }
        }

        EqNode::Sqrt(inner) => format!("sqrt({})", ast_to_plain_string(inner)),

        EqNode::Delimited {
            left,
            right,
            content,
        } => {
            let inner = ast_to_plain_string(content);

            if left == "|" && right == "|" {
                format!("abs({inner})")
            } else {
                format!("({inner})")
            }
        }

        EqNode::Limit { name, lower } => name
            .trim_start_matches("\\operatorname")
            .trim_start_matches('\\')
            .to_string(),

        EqNode::MathFont { content, .. } => ast_to_plain_string(content),

        EqNode::Brace { content, .. } => ast_to_plain_string(content),

        unsupported => panic!("Unsupported LaTeX input: {:?}", unsupported),
    }
}

fn normalise_text(s: &str) -> String {
    match s {
        "π" => "pi".to_string(),
        "−" => "-".to_string(),
        "×" | "·" | "⋅" => "*".to_string(),
        "÷" => "/".to_string(),
        _ => s
            .trim_start_matches("\\operatorname")
            .trim_start_matches('\\')
            .to_string(),
    }
}

fn seq_to_plain_string(nodes: &[EqNode]) -> String {
    // println!("Test4-2: {:?} \n\n", nodes);
    let mut res = String::new();

    let end_chars = [
        "x", "y", "z", "e", "pi", ")", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    ];

    let start_chars = [
        "x", "y", "z", "e", "pi", "(", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "\\",
        "\\left", "sqrt", "ln", "abs", "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh",
        "tanh", "asinh", "acosh", "atanh",
    ];

    for node in nodes {
        let part = ast_to_plain_string(node);
        if part.is_empty() {
            continue;
        }
        if !res.is_empty() {
            if end_chars.iter().any(|&end| res.ends_with(end)) {
                if start_chars.iter().any(|&start| part.starts_with(start)) {
                    res.push('*');
                }
            }
        }
        res.push_str(&part);
    }
    res

    // let str_nodes = nodes.iter().map(|x| ast_to_plain_string(x));
    // let merged = str_nodes.collect();
    // // println!("Test1: {}", merged);
    // merged
}
