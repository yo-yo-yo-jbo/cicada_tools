from sympy import Matrix

SQUARES = [

    # Page 3 using the GP-sums of each Runic word
    # 272        138     SHADOWS     131     151
    # AETHEREAL     BVFFERS     VOID        CARNAL      18.
    # 226        OBSCVRA     FORM        245     MOBIVS.
    # 18     ANALOG      VOID        MOVRNFVL        AETHEREAL.
    # 151        131     CABAL       138     272.
    Matrix(
        [ 272, 138, 341, 131, 151 ],
        [ 366, 199, 130, 320,  18 ],
        [ 226, 245,  91, 245, 226 ],
        [  18, 320, 130, 199, 366 ],
        [ 151, 131, 341, 138, 272 ]
    ),

    # Page 7 given as-is
    Matrtix(
        [  434, 1311,  312,  278,  966 ],
        [  204,  812,  934,  280, 1071 ],
        [  626,  620,  809,  620,  626 ],
        [ 1071,  280,  934,  812,  204 ],
        [  966,  278,  312, 1311,  434 ]
    )

    # Page 23 given as-is
    Matrix(
        [ 3258, 3222, 3152, 3038 ],
        [ 3278, 3299, 3298, 2838 ],
        [ 3288, 3294, 3296, 2472 ],
        [ 4516, 1206,  708, 1820 ],
    )
]
