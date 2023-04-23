from flask import Flask, render_template
import notebook
app = Flask(__name__)

# two decorators, same function
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', the_title='Visualization of Brain Tumor')

@app.route('/visualization.html')
def visualization():
    visualization = notebook.render()
    return render_template('visualization.html',visualization_html=visualization)

@app.route('/team.html')
def team():
    return render_template('team.html', the_title='Meet Our Team')

if __name__ == '__main__':
    app.run(debug=True)
