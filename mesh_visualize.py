import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import pylab as pl
import numpy as np

V = np.array
r2h = lambda x: colors.rgb2hex(tuple(map(lambda y: y / 255., x)))
# surface_color = r2h((255, 230, 205))
surface_color1 = r2h((255, 255, 0))
surface_color2 = r2h((0,255,255))
edge_color = r2h((90, 90, 90))
edge_colors = (r2h((15, 167, 175)), r2h((230, 81, 81)), r2h((142, 105, 252)), r2h((248, 235, 57)),
			   r2h((51, 159, 255)), r2h((225, 117, 231)), r2h((97, 243, 185)), r2h((161, 183, 196)))




def init_plot():
	ax = pl.figure().add_subplot(111, projection='3d')
	# hide axis, thank to
	# https://stackoverflow.com/questions/29041326/3d-plot-with-matplotlib-hide-axes-but-keep-axis-labels/
	ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
	ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
	ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
	# Get rid of the spines
	ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
	ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
	ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
	# Get rid of the ticks
	ax.set_xticks([])
	ax.set_yticks([])
	ax.set_zticks([])
	return (ax, [np.inf, -np.inf, np.inf, -np.inf, np.inf, -np.inf])


def update_lim(mesh,idx, plot):
	vs = mesh[0]
	for i in range(3):
		plot[1][2 * i] = min(plot[1][2 * i], vs[:, i].min())
		plot[1][2 * i + 1] = max(plot[1][2 * i], vs[:, i].max())
	return plot


def update_plot(mesh,idx,plot):
	if plot is None:
		plot = init_plot()
	return update_lim(mesh,idx, plot)


def surfaces(mesh,idx, plot):
	
	vs, faces, edges = mesh
	print(vs)
	vtx = vs[faces]
	edgecolor = edge_color if not len(edges) else 'none'
	if idx==0:
		color=surface_color1
	else:
		color=surface_color2
	tri = a3.art3d.Poly3DCollection(vtx, facecolors=color +'55', edgecolors=edgecolor,
									linewidths=.5, linestyles='dashdot')
	plot[0].add_collection3d(tri)
	return plot


def segments(mesh,idx, plot):
	vs, _, edges = mesh
	for edge_c, edge_group in enumerate(edges):
		for edge_idx in edge_group:
			edge = vs[edge_idx]
			line = a3.art3d.Line3DCollection([edge],  linewidths=.5, linestyles='dashdot')
			line.set_color(edge_colors[edge_c % len(edge_colors)])
			plot[0].add_collection3d(line)
	return plot


def plot_mesh(mesh,idx,pt, *whats, show=True, plot=None):
	for what in [update_plot] + list(whats):
		plot = what(mesh,idx, plot)
	if show:
		li = max(plot[1][1], plot[1][3], plot[1][5])
		plot[0].auto_scale_xyz([0, li], [0, li], [0, li])
		pl.tight_layout()
		
		pl.annotate("this",xy=(pt[0],pt[1]))

		pl.show()
		pl.savefig('mesh.jpg')
	return plot


def parse_obje(obj_file, scale_by):
	vs = []
	faces = []
	edges = []

	def add_to_edges():
		if edge_c >= len(edges):
			for _ in range(len(edges), edge_c + 1):
				edges.append([])
		edges[edge_c].append(edge_v)

	def fix_vertices():
		nonlocal vs, scale_by
		vs = V(vs)
		z = vs[:, 2].copy()
		vs[:, 2] = vs[:, 1]
		vs[:, 1] = z
		max_range = 0
		for i in range(3):
			min_value = np.min(vs[:, i])
			max_value = np.max(vs[:, i])
			max_range = max(max_range, max_value - min_value)
			vs[:, i] -= min_value
		if not scale_by:
			scale_by = max_range
		vs /= scale_by

	with open(obj_file) as f:
		for line in f:
			line = line.strip()
			splitted_line = line.split()
			if not splitted_line:
				continue
			elif splitted_line[0] == 'v':
				vs.append([float(v) for v in splitted_line[1:4]])
			
			elif splitted_line[0] == 'f':
				
				faces.append([int(c) - 1 for c in splitted_line[1:]])
			elif splitted_line[0] == 'e':

				if len(splitted_line) >= 4:
					edge_v = [int(c) - 1 for c in splitted_line[1:-1]]
					edge_c = int(splitted_line[-1])
					add_to_edges()

	vs = V(vs)
	fix_vertices()
	faces = V(faces, dtype=int)
	edges = [V(c, dtype=int) for c in edges]
	return (vs, faces, edges), scale_by


def view_meshes(files, offset=.2):
	plot = None
	max_x = 0
	scale = 0
	for idx,file in enumerate(files):
		mesh, scale = parse_obje(file, scale)
		
		max_x_current = mesh[0][:, 0].max()
		mesh[0][:, 0] += max_x + offset
		
		plot = plot_mesh(mesh,idx,mesh[0][0], surfaces, segments, plot=plot, show=file == files[-1])
		max_x += max_x_current + offset


if __name__=='__main__':
	import argparse
	parser = argparse.ArgumentParser("view meshes")
	parser.add_argument('--files', nargs='+', default=[''], type=str,
						help="list of 1 or more .obj files")
	args = parser.parse_args()

	# view meshes
	meshes = ['648518346341351924.obj', '648518346341353526.obj']
	view_meshes(['/usr/people/smondal/seungmount/research/smondal/pinky_meshes/'+m for m in meshes])

