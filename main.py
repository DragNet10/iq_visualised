#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vtk
import math
import vtk_3d_line_plt.line as vtk_line

"""
There are two alternative ways to apply the transform.
 1) Use vtkTransformPolyDataFilter to create a new transformed polydata.
    This method is useful if the transformed polydata is needed
      later in the pipeline
    To do this, set USER_MATRIX = True
 2) Apply the transform directly to the actor using vtkProp3D's SetUserMatrix.
    No new data is produced.
    To do this, set USER_MATRIX = False
"""


class vtkTimerCallback():
    def __init__(self, steps, renderer, iren, *renderWindowInteractor, localmovieWriter, localimageFilter):
        self.timer_count = 0
        self.steps = steps
        self.renderer = renderer
        self.iren = iren
        self.timerId = None
        self.actor_lines = renderWindowInteractor
        self.actor_lines_1 = renderWindowInteractor
        self.localmovieWriter = localmovieWriter
        self.localimageFilter = localimageFilter

    def execute(self, obj, event):
        frequency = 0.05
        quantity_of_segments = 20
        quantity_of_full_rotations = 3
        phase_step_resolution_divisor = 50
        datapoint_sample_rate = frequency * \
            quantity_of_segments/phase_step_resolution_divisor

        # Initialize plot data
        data_points = [[0.0, 0.0, 0.0] for i in range(
            quantity_of_segments*quantity_of_full_rotations)]
        data_points_1 = [[0.0, 0.0, 0.0] for i in range(
            quantity_of_segments * quantity_of_full_rotations)]
        # Calculation Loop
        for i in range(len(data_points)):
            data_points[i] = [math.sin(i * 2 * math.pi / quantity_of_segments - self.timer_count*math.pi / phase_step_resolution_divisor),
                              math.cos(i * 2 * math.pi / quantity_of_segments - self.timer_count*math.pi / phase_step_resolution_divisor), -i*datapoint_sample_rate]

            data_points_1[i] = [math.cos(i * 2 * math.pi / quantity_of_segments - self.timer_count * math.pi / phase_step_resolution_divisor + math.pi / 2),
                                math.sin(i * 2 * math.pi / quantity_of_segments - self.timer_count * math.pi / phase_step_resolution_divisor + math.pi / 2), -i * datapoint_sample_rate]

        vtk_line.vtk_clear_line(self.renderer, self.actor_lines)
        vtk_line.vtk_clear_line(self.renderer, self.actor_lines_1)

        # Render new lines
        self.actor_lines = vtk_line.vtk_points_to_line(
            self.renderer, data_points)
        self.actor_lines_1 = vtk_line.vtk_points_to_line(
            self.renderer, data_points_1, color=[253 / 255, 203 / 255, 51 / 255])

        iren = obj
        iren.GetRenderWindow().Render()
        self.timer_count += 1

        # Export a single frame
        self.localimageFilter.Modified()
        self.localmovieWriter.Write()

        if self.timer_count == self.steps:
            # Finish movie
            self.localmovieWriter.End()

        return


def main():
    colors = vtk.vtkNamedColors()

    # input -> data points
    #   Calculate the start and end of each link
    #   Generate a list of links
    #   Auto scale the graph based on max link
    #   render axies
    #   render links

    # Create a renderer, render window, and interactor
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName('3D IQ Representation')
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindow.FullScreenOn()
    vtk_line.vtk_generate_axis(renderer)

    # Move camera and generate axes
    renderer.GetActiveCamera().Azimuth(60)
    renderer.GetActiveCamera().Elevation(30)
    renderer.ResetCamera()
    renderWindow.SetWindowName('Axes')
    renderer.SetBackground(colors.GetColor3d('BkgColor'))

    # Render and interact
    renderWindow.Render()
    renderer.GetActiveCamera().Zoom(1.3)

    # Initialize must be called prior to creating timer events.
    renderWindowInteractor.Initialize()
    imageFilter = vtk.vtkWindowToImageFilter()
    imageFilter.SetInput(renderWindow)
    imageFilter.SetInputBufferTypeToRGB()
    imageFilter.ReadFrontBufferOff()
    imageFilter.Update()

    # Setup movie writer
    moviewriter = vtk.vtkOggTheoraWriter()
    moviewriter.SetInputConnection(imageFilter.GetOutputPort())
    moviewriter.SetFileName("movie.ogv")
    moviewriter.Start()
    # Sign up to receive TimerEvent
    number_of_callbacks = 3000
    cb = vtkTimerCallback(number_of_callbacks,  renderer, renderWindowInteractor,
                          localmovieWriter=moviewriter, localimageFilter=imageFilter)
    renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
    cb.timerId = renderWindowInteractor.CreateRepeatingTimer(5)

    # start the interaction and timer
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()
