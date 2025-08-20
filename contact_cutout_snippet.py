# Bottom drain contacts + M1 bars + labels
x0 = 0
for i in range(self.n):
    od_left  = x0
    od_right = x0 + (self.l_nm + 2*self.sd_ext_nm)          # window width along X

    usable_w     = (od_right - od_left) - 2*self.cont_enc_od_nm
    n_cuts       = max(1, (usable_w + (self.cont_pitch_nm - self.cont_size_nm)) // self.cont_pitch_nm)
    total_cuts_w = n_cuts * self.cont_pitch_nm - (self.cont_pitch_nm - self.cont_size_nm)
    start_x      = od_left + self.cont_enc_od_nm + ((usable_w - total_cuts_w) // 2) + self.cont_size_nm // 2

    # place CO cuts
    for k in range(n_cuts):
        cx = start_x + k * self.cont_pitch_nm
        shapes(ly_co).insert(self._ico_nm(cx, drain_co_y, self.cont_size_nm, dbu))

    # M1 landing bar that covers the row of contacts
    m1_y0 = drain_co_y - (self.cont_size_nm // 2 + self.cont_enc_m1_nm)
    m1_y1 = drain_co_y + (self.cont_size_nm // 2 + self.cont_enc_m1_nm)
    m1_x0 = start_x - self.cont_size_nm // 2 - self.cont_enc_m1_nm
    m1_x1 = start_x + (n_cuts - 1) * self.cont_pitch_nm + self.cont_size_nm // 2 + self.cont_enc_m1_nm
    shapes(ly_m1).insert(self._ibox_nm(m1_x0, m1_y0, m1_x1, m1_y1, dbu))

