import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "<Title: {}>".format(self.title)

@app.route("/", methods=["GET", "POST"])
def home():
    books = Book.query.all()  # Obter todos os livros
    error_message = None      # Variável para mensagem de erro

    if request.method == "POST" and request.form:
        title = request.form.get("title")
        
        # Verifica duplicidade de título
        existing_book = Book.query.filter_by(title=title).first()
        if existing_book:
            error_message = f"O livro '{title}' já existe no sistema."  # Define mensagem de erro
            print("Tentativa de adicionar título duplicado:", title)  # Verificação extra
        else:
            try:
                book = Book(title=title)
                db.session.add(book)
                db.session.commit()
                books = Book.query.all()  # Atualiza lista de livros
            except Exception as e:
                db.session.rollback()
                error_message = "Falha ao adicionar o livro. Tente novamente."
                print("Erro ao adicionar livro:", e)

    return render_template("home.html", books=books, error_message=error_message)

@app.route("/update", methods=["POST"])
def update():
    newtitle = request.form.get("newtitle")
    oldtitle = request.form.get("oldtitle")
    
    # Verifica se o novo título já existe
    existing_book = Book.query.filter_by(title=newtitle).first()
    if existing_book:
        error_message = f"O livro '{newtitle}' já existe no sistema."  # Define mensagem de erro
        print("Tentativa de alterar para título duplicado:", newtitle)  # Verificação extra
        return redirect("/")  # Retorna para a página inicial, mas não atualiza

    try:
        book = Book.query.filter_by(title=oldtitle).first()
        if book:
            book.title = newtitle
            db.session.commit()
        else:
            print(f"Livro com título '{oldtitle}' não encontrado.")
    except Exception as e:
        db.session.rollback()
        print("Couldn't update book title:", e)

    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
