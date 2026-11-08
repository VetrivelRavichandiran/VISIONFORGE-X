// VISIONFORGE X - Sobel Edge Detection IP Core
// 3x3 Sobel operator for edge detection on AXI4-Stream video
// Target: Xilinx Zynq-7010 (ZYBO Z7-10)

`timescale 1ns / 1ps

module sobel_edge #(
    parameter PIXEL_WIDTH = 8,
    parameter LINE_BUFFER_DEPTH = 640  // Max line width
)(
    input  wire             aclk,
    input  wire             aresetn,

    // AXI4-Stream Input (Grayscale)
    input  wire             s_axis_tvalid,
    output wire             s_axis_tready,
    input  wire [7:0]       s_axis_tdata,
    input  wire             s_axis_tlast,

    // AXI4-Stream Output (Edge magnitude)
    output wire             m_axis_tvalid,
    input  wire             m_axis_tready,
    output wire [8:0]       m_axis_tdata,  // 9-bit magnitude
    output wire             m_axis_tlast,

    // AXI-Lite Control Registers
    input  wire             s_axi_aclk,
    input  wire             s_axi_aresetn,
    input  wire             s_axi_awaddr,
    input  wire             s_axi_awvalid,
    output wire             s_axi_awready,
    input  wire [31:0]      s_axi_wdata,
    input  wire             s_axi_wvalid,
    output wire             s_axi_wready,
    output wire             s_axi_bresp,
    output wire             s_axi_bvalid,
    input  wire             s_axi_bready,
    input  wire             s_axi_araddr,
    input  wire             s_axi_arvalid,
    output wire             s_axi_arready,
    output wire [31:0]      s_axi_rdata,
    output wire             s_axi_rresp,
    output wire             s_axi_rvalid,
    input  wire             s_axi_rready
);

    // Register addresses
    localparam REG_THRESHOLD = 32'd0;
    localparam REG_ENABLE    = 32'd4;
    localparam REG_STATUS    = 32'd8;
    localparam REG_FRAME_CNT = 32'd12;

    // Line buffer for 3x3 window
    reg [7:0] line_buffer [0:LINE_BUFFER_DEPTH-1];
    reg [7:0] row0, row1, row2;
    reg [7:0] col0, col1, col2;

    // Sobel kernels
    // Gx = [-1 0 1; -2 0 2; -1 0 1]
    // Gy = [-1 -2 -1; 0 0 0; 1 2 1]

    reg [10:0] gx, gy;
    reg [10:0] magnitude;

    // Control registers
    reg [7:0] threshold_reg;
    reg enable_reg;
    reg [31:0] frame_count;

    // Line buffer shift register
    always @(posedge aclk) begin
        if (!aresetn) begin
            frame_count <= 32'd0;
            enable_reg <= 1'b0;
            threshold_reg <= 8'd0;
        end
        else if (s_axi_awvalid && s_axi_awaddr[3:2] == 2'b00) begin
            // Write control registers
            case (s_axi_awaddr[3:2])
                2'b00: threshold_reg <= s_axi_wdata[7:0];
                2'b01: enable_reg <= s_axi_wdata[0];
            endcase
        end
        else if (s_axis_tvalid && s_axis_tready) begin
            // Shift line buffer
            for (int i = 0; i < LINE_BUFFER_DEPTH-1; i = i + 1)
                line_buffer[i] <= line_buffer[i+1];
            line_buffer[LINE_BUFFER_DEPTH-1] <= s_axis_tdata;

            if (s_axis_tlast)
                frame_count <= frame_count + 1;
        end
    end

    // 3x3 window extraction
    // In a real implementation, this would use proper line buffers
    // For synthesis, use FIFO-based line delay

    // Sobel convolution (simplified - actual impl needs proper windowing)
    always @(posedge aclk) begin
        if (!aresetn || !enable_reg) begin
            magnitude <= 11'd0;
        end
        else if (s_axis_tvalid && s_axis_tready) begin
            // Simplified edge detection (gradient approximation)
            gx <= {1'b0, s_axis_tdata} - {1'b0, line_buffer[LINE_BUFFER_DEPTH-3]};
            gy <= {1'b0, line_buffer[LINE_BUFFER_DEPTH-1]} - {1'b0, line_buffer[LINE_BUFFER_DEPTH-5]};
            magnitude <= (gx > gy) ? gx : gy;
        end
    end

    // Output
    assign m_axis_tvalid = s_axis_tvalid && enable_reg;
    assign s_axis_tready = m_axis_tready;
    assign m_axis_tdata = magnitude[8:0];
    assign m_axis_tlast = s_axis_tlast;

    // AXI-Lite read
    assign s_axi_awready = 1'b1;
    assign s_axi_wready = 1'b1;
    assign s_axi_bresp = 2'b00;
    assign s_axi_bvalid = s_axi_awvalid;
    assign s_axi_arready = 1'b1;
    assign s_axi_rvalid = s_axi_arvalid;
    assign s_axi_rresp = 2'b00;
    assign s_axi_rdata = (s_axi_araddr[3:2] == 2'b10) ? {24'd0, frame_count} :
                         (s_axi_araddr[3:2] == 2'b01) ? {24'd0, enable_reg} :
                         {24'd0, threshold_reg};

endmodule
