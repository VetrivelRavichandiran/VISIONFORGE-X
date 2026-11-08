// VISIONFORGE X - Grayscale Conversion IP Core
// Converts RGB video stream to grayscale using AXI4-Stream interface
// Target: Xilinx Zynq-7010 (ZYBO Z7-10)

`timescale 1ns / 1ps

module grayscale_conv #(
    parameter DATA_WIDTH = 24,  // 8 bits per color channel
    parameter AXIS_TDATA_WIDTH = 24
)(
    // AXI4-Stream Input (RGB)
    input  wire                        s_axis_aclk,
    input  wire                        s_axis_aresetn,
    input  wire                        s_axis_tvalid,
    output wire                        s_axis_tready,
    input  wire [AXIS_TDATA_WIDTH-1:0] s_axis_tdata,
    input  wire                        s_axis_tlast,

    // AXI4-Stream Output (Grayscale)
    output wire                        m_axis_tvalid,
    input  wire                        m_axis_tready,
    output wire [7:0]                  m_axis_tdata,
    output wire                        m_axis_tlast
);

    // RGB to Grayscale conversion using ITU-R BT.601 coefficients
    // Y = 0.299*R + 0.587*G + 0.114*B
    // Using fixed-point: Y = (77*R + 150*G + 29*B) >> 8

    reg [7:0] r_ch, g_ch, b_ch;
    reg [15:0] gray_val;

    // Extract color channels from 24-bit RGB
    always @(posedge s_axis_aclk) begin
        if (!s_axis_aresetn) begin
            r_ch <= 8'd0;
            g_ch <= 8'd0;
            b_ch <= 8'd0;
        end
        else if (s_axis_tvalid && s_axis_tready) begin
            r_ch <= s_axis_tdata[23:16];
            g_ch <= s_axis_tdata[15:8];
            b_ch <= s_axis_tdata[7:0];
        end
    end

    // Grayscale calculation
    always @(posedge s_axis_aclk) begin
        if (!s_axis_aresetn) begin
            gray_val <= 16'd0;
        end
        else if (s_axis_tvalid && s_axis_tready) begin
            gray_val <= (77 * {1'b0, r_ch} +
                        150 * {1'b0, g_ch} +
                        29 * {1'b0, b_ch}) >>> 8;
        end
    end

    // Output assignment
    assign m_axis_tvalid = s_axis_tvalid;
    assign s_axis_tready = m_axis_tready;
    assign m_axis_tdata = gray_val[7:0];
    assign m_axis_tlast = s_axis_tlast;

endmodule
