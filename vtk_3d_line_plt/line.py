import vtk

USER_MATRIX = True
def shift_right_and_insert_at_start(arr, insert):
    n = len(arr)
    # for i in range(0, n):
    for j in range(len(arr) - 1, -1, -1):
        # Shift element of array by one
        arr[j] = arr[j - 1]

        # insert variable will be added to the start of the array.
    arr[0] = insert
    return arr


def vtk_generate_link(startPoint, endPoint, diameter, color):
    # Create a cylinder.
    # Cylinder height vector is (0,1,0).
    # Cylinder center is in the middle of the cylinder
    cylinderSource = vtk.vtkCylinderSource()
    cylinderSource.SetResolution(6)

    # Compute a basis
    normalizedX = [0] * 3
    normalizedY = [0] * 3
    normalizedZ = [0] * 3

    # The X axis is a vector from start to end
    vtk.vtkMath.Subtract(endPoint, startPoint, normalizedX)
    length = vtk.vtkMath.Norm(normalizedX)+vtk.vtkMath.Norm(normalizedX)*0.05
    vtk.vtkMath.Normalize(normalizedX)

    arbitrary = [0, 1, 0]
    vtk.vtkMath.Cross(normalizedX, arbitrary, normalizedZ)
    vtk.vtkMath.Normalize(normalizedZ)

    # The Y axis is Z cross X
    vtk.vtkMath.Cross(normalizedZ, normalizedX, normalizedY)
    matrix = vtk.vtkMatrix4x4()

    # Create the direction cosine matrix
    matrix.Identity()
    for i in range(0, 3):
        matrix.SetElement(i, 0, normalizedX[i])
        matrix.SetElement(i, 1, normalizedY[i])
        matrix.SetElement(i, 2, normalizedZ[i])

    # Apply the transforms
    transform = vtk.vtkTransform()
    transform.Translate(startPoint)  # translate to starting point
    transform.Concatenate(matrix)  # apply direction cosines
    transform.RotateZ(-90.0)  # align cylinder to x axis
    transform.Scale(diameter, length, diameter)  # scale along the height vector
    transform.Translate(0, .5, 0)  # translate to start of cylinder

    # Transform the polydata
    transformPD = vtk.vtkTransformPolyDataFilter()
    transformPD.SetTransform(transform)
    transformPD.SetInputConnection(cylinderSource.GetOutputPort())

    # Create a mapper and actor for the arrow
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()
    if USER_MATRIX:
        mapper.SetInputConnection(cylinderSource.GetOutputPort())
        actor.SetUserMatrix(transform.GetMatrix())
    else:
        mapper.SetInputConnection(transformPD.GetOutputPort())
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)

    return actor

def vtk_generate_line_head(head_center, diameter, color,diameter_scale = 2,sphere_ang_res = 10):
    #Make a head for the line.
    sphereEndSource = vtk.vtkSphereSource()
    sphereEndSource.SetRadius(diameter*diameter_scale)
    sphereEndSource.SetThetaResolution(sphere_ang_res)
    sphereEndSource.SetPhiResolution(sphere_ang_res)
    sphereEndMapper = vtk.vtkPolyDataMapper()
    sphereEndMapper.SetInputConnection(sphereEndSource.GetOutputPort())
    sphereEnd = vtk.vtkActor()
    sphereEnd.SetMapper(sphereEndMapper)
    sphereEnd.GetProperty().SetColor(color)
    sphereEndSource.SetCenter(head_center)
    return sphereEnd


def vtk_points_to_line(renderer, data_points, diameter=0.05, color = [150.5 / 255, 30 / 255, 255 / 255]):
    links_to_render = [vtk.vtkActor()] * (len(data_points)+1) #Number of links to render. +1 for the head of the line
    links_to_render[0] = vtk_generate_line_head(data_points[0], diameter, color) #Add head
    renderer.AddActor(links_to_render[0])
    for i in range(len(data_points)-1, 0, -1): #step through and add each link
        links_to_render[i] = vtk_generate_link(data_points[i], data_points[i - 1], diameter, color)
        renderer.AddActor(links_to_render[i])
    return links_to_render


def vtk_clear_line(renderer, actors_to_remove):
    #Actors are fed in as a list nested in a list.
    for j in range(0, len(actors_to_remove)):#Interate over each of the actors and remove them from being rendered
        renderer.RemoveActor(actors_to_remove[j])


def vtk_generate_axis(renderer, axis_scale=1.5):
    # Render Axis
    axes_pos = vtk.vtkAxesActor()

    transform_pos = vtk.vtkTransform()
    transform_pos.Scale([axis_scale, axis_scale, axis_scale])
    axes_pos.SetUserTransform(transform_pos)
    axes_pos.SetConeResolution(4)
    axes_pos.SetShaftTypeToCylinder()
    axes_pos.SetXAxisLabelText("I")
    axes_pos.SetYAxisLabelText("Q")
    axes_pos.SetZAxisLabelText("t")

    axes_pos.SetCylinderRadius(0.015)
    axes_pos.SetConeRadius(0.3)

    renderer.AddActor(axes_pos)

    axes_neg = vtk.vtkAxesActor()

    axes_neg.SetXAxisLabelText("")
    axes_neg.SetYAxisLabelText("")
    axes_neg.SetZAxisLabelText("")

    axes_neg.SetConeRadius(0.3)


    transform = vtk.vtkTransform()
    transform.RotateZ(180)
    transform.Scale([axis_scale, axis_scale, -axis_scale])

    axes_neg.SetUserTransform(transform)
    axes_neg.SetConeResolution(4)

    axes_neg.SetCylinderRadius(0.015)
    renderer.AddActor(axes_neg)
