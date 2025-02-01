
from flask import Flask, render_template, request, current_app, redirect

def map(cursor, connection, args):
    args["title"] = "Карта"