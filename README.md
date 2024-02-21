<div align="center">
    <h1>CompilationBenchmark</h1>
    <p>Compilers and one-core performance tester for Linux-based systems.</p>
    <p>
        <a href="https://github.com/HyperWinX/CompilationBenchmark/graphs/contributors">
            <img src="https://img.shields.io/github/contributors/HyperWinX/CompilationBenchmark" alt="contributors"/>
        </a>
        <a href="https://github.com/HyperWinX/CompilationBenchmark/commits/master">
            <img src="https://img.shields.io/github/last-commit/HyperWinX/CompilationBenchmark" alt="last commit"/>
        </a>
        <a href="https://github.com/HyperWinX/CompilationBenchmark/network/members">
            <img src="https://img.shields.io/github/forks/HyperWinX/CompilationBenchmark" alt="forks"/>
        </a>
        <a href="https://github.com/HyperWinX/CompilationBenchmark/stargazers">
            <img src="https://img.shields.io/github/stars/HyperWinX/CompilationBenchmark" alt="contributors"/>
        </a>
        <a href="https://github.com/HyperWinX/CompilationBenchmark/issues">
            <img src="https://img.shields.io/github/issues/HyperWinX/CompilationBenchmark" alt="contributors"/>
        </a>
    </p>
</div>
<br/>

# Contents
- [About project](#about-project)
- [Default configutation](#default-configuration)
- [Usage](#usage)

## About project
This is a small benchmark written in Python, and can measure one-core performance of compilers on big code blocks.

## Default configuration
All languages: C, C++, ASM, Rust, Zig
Code size: 100.000 lines of code

## Usage
Run with default configuration:
```
python3 bench.py
```
Optional arguments:
```
python3 bench.py --languages=c,cpp --lines=500000
```
--languages argument will set which languages to test. Supported codes: c, cpp, asm, rust, zig  
--lines arguments will set count of code lines to compile for every language.